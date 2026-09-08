"""TR-003r anchor library. Certified by tests/test_anchors.py before
any real embedding passes through (ARENA rule 4; TR-002r D11 pattern).

C3 relative representations: each side expressed as cosines to its own
embedding of the SAME anchor texts; no fitted transform (Moschella).
C4 paired-anchor orthogonal Procrustes: the ceiling instrument. Both
sides centered on their anchor means and reduced by PCA fit on the
anchors themselves to rank r = min(d_src, d_tgt, k); the reader side
owns nothing but its anchors and queries, so nothing else may fit
(DECISIONS D10). C2 naive: raw vectors, a seeded random map only where
dimensions differ. Control 3: independent seeded random projections
of rank k on each side.
"""
import numpy as np


def unit(X):
    X = np.asarray(X, dtype=np.float64)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def relative(X, anchors):
    """(n, k) cosine-to-anchor coordinates."""
    return unit(X) @ unit(anchors).T


def procrustes_map(anchors_src, anchors_tgt):
    """Return (f_src, f_tgt): maps from each raw space to a common frame."""
    As, At = np.asarray(anchors_src, float), np.asarray(anchors_tgt, float)
    k = len(As)
    if len(At) != k:
        raise ValueError("anchors must be paired")
    mu_s, mu_t = As.mean(0), At.mean(0)
    r = min(As.shape[1], At.shape[1], k)

    def pca(A, mu):
        _, _, Vt = np.linalg.svd(A - mu, full_matrices=False)
        return Vt[:r]
    Ps, Pt = pca(As, mu_s), pca(At, mu_t)
    Zs, Zt = (As - mu_s) @ Ps.T, (At - mu_t) @ Pt.T
    U, _, Vt = np.linalg.svd(Zs.T @ Zt)
    W = U @ Vt
    return (lambda X: ((np.asarray(X, float) - mu_s) @ Ps.T) @ W,
            lambda X: (np.asarray(X, float) - mu_t) @ Pt.T)


def random_map(d_in, d_out, seed):
    rng = np.random.default_rng(seed)
    if d_out <= d_in:
        Q, _ = np.linalg.qr(rng.standard_normal((d_in, d_in)))
        return Q[:, :d_out]
    return rng.standard_normal((d_in, d_out)) / np.sqrt(d_in)


def naive_map(X_src, d_tgt, seed):
    """C2 floor: raw vectors; a seeded random map only where dims differ."""
    X_src = np.asarray(X_src, float)
    if X_src.shape[1] == d_tgt:
        return X_src
    return X_src @ random_map(X_src.shape[1], d_tgt, seed)


def random_projection_pair(d_a, d_b, k, seed):
    """Control 3: independent rank-k projections, one per side."""
    return random_map(d_a, k, seed), random_map(d_b, k, seed + 1)
