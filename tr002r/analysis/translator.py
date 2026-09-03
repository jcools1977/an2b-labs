"""The frozen primary translator (protocol amendment three, D3),
certified by the D11 exam before any real embedding passes through.

Faithful implementation of mini-vec2vec (arXiv:2510.02348, Listings
1-2, fetched at implementation time after the D11 exam refuted three
reconstructions from memory; the chain is logged in DECISIONS):
1. Preprocess: center each space, project rows to the unit
   hypersphere (wide spaces first PCA-reduced to 384 on their own
   half, per D3).
2. Approximate matching, ensembled over runs: k-means in each space;
   centroid permutation on the two centroid cosine-similarity
   matrices by seeded greedy structural growth (the exam caught
   scipy's FAQ solver returning objectives far below the known-true
   permutation's; see _match_centroids); per-point
   RELATIVE representations against the aligned centroids,
   concatenated across runs.
3. Initial transformation: pseudo-pairs send each A point to the
   average of its k nearest B points in relative space; orthogonal
   Procrustes on the pairs.
4. Refine-1: subsampled ICP (kNN in ambient B space, averaged
   neighbors, Procrustes) with exponential smoothing, many rounds.
5. Refine-2: exactly ONE cluster-based correction (k-means on A;
   k-means on B initialized from the transported A centroids;
   Procrustes on centroid pairs; smoothed), per the paper's finding
   that more than one dilutes the signal.
Deterministic given the seed. No paired documents are ever used.
"""
import numpy as np
from sklearn.cluster import KMeans

TARGET_DIM = 384
NUM_RUNS, NUM_CLUSTERS, KNN_REL = 8, 40, 10
R1_ITERS, R1_SUB, R1_K2, ALPHA = 60, 2000, 5, 0.3
R2_CLUSTERS = 64


class _Space:
    def __init__(self, X):
        X = np.asarray(X, float)
        self.pca_mu, self.pca = None, None
        if X.shape[1] > TARGET_DIM:
            self.pca_mu = X.mean(0)
            Xc = X - self.pca_mu
            _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
            self.pca = Vt[:TARGET_DIM]
            X = Xc @ self.pca.T
        self.mu = X.mean(0)
        self.Z = self._sphere(X - self.mu)

    @staticmethod
    def _sphere(X):
        return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)

    def transform(self, X):
        X = np.asarray(X, float)
        if self.pca is not None:
            X = (X - self.pca_mu) @ self.pca.T
        return self._sphere(X - self.mu)


def _procrustes(A, B):
    U, _, Vt = np.linalg.svd(A.T @ B)
    return U @ Vt


def _cos_rows(X, C):
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    return Xn @ Cn.T


def _match_centroids(SA, SB, n_seeds=64):
    """Seeded greedy structural growth: pin a candidate pair, extend
    by maximal consistency with everything pinned (running matrix M),
    score complete matchings by the QAP objective, keep the best.
    Replaces scipy's FAQ, which the D11 exam caught returning
    objectives far below the known-true permutation's."""
    k = len(SA)
    prof_a = np.sort(SA, axis=1)
    prof_b = np.sort(SB, axis=1)
    corr = np.corrcoef(np.vstack([prof_a, prof_b]))[:k, k:]
    flat = np.argsort(corr.ravel())[::-1][:n_seeds]
    seeds = [(int(f // k), int(f % k)) for f in flat]

    def grow(si, sj):
        perm = np.full(k, -1)
        used_b = np.zeros(k, bool)
        M = np.zeros((k, k))
        def pin(i, j):
            perm[i] = j
            used_b[j] = True
            M[:] += np.outer(SA[:, i], SB[:, j])
            M[i, :] = -np.inf
            M[:, used_b] = -np.inf
        pin(si, sj)
        for _ in range(k - 1):
            i, j = np.unravel_index(np.argmax(M), M.shape)
            pin(int(i), int(j))
        return perm

    def score(perm):
        return float((SA * SB[np.ix_(perm, perm)]).sum())
    best, bestobj = None, -np.inf
    for si, sj in seeds:
        p = grow(si, sj)
        o = score(p)
        if o > bestobj:
            best, bestobj = p, o
    return best


def _anchor_relative(A, B, seed):
    """Ensembled relative representations (paper section 3.2)."""
    RA, RB = [], []
    for r in range(NUM_RUNS):
        ka = KMeans(n_clusters=NUM_CLUSTERS, random_state=seed + r,
                    n_init=2).fit(A)
        kb = KMeans(n_clusters=NUM_CLUSTERS, random_state=seed + r,
                    n_init=2).fit(B)
        ca, cb = ka.cluster_centers_, kb.cluster_centers_
        SA, SB = _cos_rows(ca, ca), _cos_rows(cb, cb)
        perm = _match_centroids(SA, SB)
        RA.append(_cos_rows(A, ca))
        RB.append(_cos_rows(B, cb[perm]))
    return np.hstack(RA), np.hstack(RB)


def _pseudo_pair_targets(RA, RB, B, k):
    """Each A point's target: mean of its k relative-space NNs' B
    vectors (paper section 3.3), computed in row blocks."""
    RAn = RA / (np.linalg.norm(RA, axis=1, keepdims=True) + 1e-12)
    RBn = RB / (np.linalg.norm(RB, axis=1, keepdims=True) + 1e-12)
    out = np.empty((len(RA), B.shape[1]))
    for lo in range(0, len(RA), 2048):
        hi = min(lo + 2048, len(RA))
        sims = RAn[lo:hi] @ RBn.T
        nn = np.argpartition(-sims, k, axis=1)[:, :k]
        out[lo:hi] = B[nn].mean(axis=1)
    return out


def train_translator(A_half, B_half, seed=41):
    sa, sb = _Space(A_half), _Space(B_half)
    A, B = sa.Z, sb.Z
    d = min(A.shape[1], B.shape[1])
    A, B = A[:, :d], B[:, :d]
    rng = np.random.default_rng(seed)

    RA, RB = _anchor_relative(A, B, seed)
    targets = _pseudo_pair_targets(RA, RB, B, KNN_REL)
    W = _procrustes(A, targets)

    # Refine-1: smoothed subsampled ICP with averaged neighbors
    for _ in range(R1_ITERS):
        idx = rng.choice(len(A), min(R1_SUB, len(A)), replace=False)
        As = A[idx]
        sims = (As @ W) @ B.T
        nn = np.argpartition(-sims, R1_K2, axis=1)[:, :R1_K2]
        matched = B[nn].mean(axis=1)
        W = (1 - ALPHA) * W + ALPHA * _procrustes(As, matched)

    # Refine-2: exactly one cluster-based correction
    k2 = min(R2_CLUSTERS, len(A) // 20, len(B) // 20)
    ka = KMeans(n_clusters=k2, random_state=seed, n_init=2).fit(A)
    kb = KMeans(n_clusters=k2, random_state=seed, n_init=1,
                init=ka.cluster_centers_ @ W, max_iter=50).fit(B)
    W = (1 - ALPHA) * W + ALPHA * _procrustes(ka.cluster_centers_,
                                              kb.cluster_centers_)
    return {"sa": sa, "sb": sb, "W": W, "d": d}


def apply_translator(T, X):
    Z = T["sa"].transform(X)[:, :T["d"]]
    return Z @ T["W"]


def target_space(T, X):
    """Project raw target-space vectors into the comparison frame."""
    return T["sb"].transform(X)[:, :T["d"]]
