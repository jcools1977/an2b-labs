"""Local intrinsic dimension estimators (D4), certified by the D5/D11
exam (clean and noisy synthetic manifolds) before any real embedding
may pass through them.

twonn: Facco et al. Two-NN with the standard 10% mu-tail discard,
maximum-likelihood slope through the origin.
mle: Levina-Bickel with k = min(10, n-2), averaged over points.
Both return a single scalar for a cloud (n, dim).
"""
import numpy as np
from scipy.spatial.distance import pdist, squareform


def _dists(X):
    D = squareform(pdist(np.asarray(X, dtype=float)))
    np.fill_diagonal(D, np.inf)
    return D


def twonn(X):
    # Facco et al.: fit -log(1 - F(mu)) = d * log(mu) through the
    # origin over the smallest 90% of mu values (cumulative fit, not
    # the truncated Pareto closed form, which biases upward).
    D = _dists(X)
    part = np.partition(D, 1, axis=1)[:, :2]
    r1, r2 = part[:, 0], part[:, 1]
    mu = np.sort(r2 / np.maximum(r1, 1e-12))
    n = len(mu)
    keep = int(np.floor(n * 0.9))
    F = np.arange(1, n + 1) / n
    x = np.log(np.maximum(mu[:keep], 1.0 + 1e-12))
    y = -np.log(np.maximum(1.0 - F[:keep], 1e-12))
    denom = float(x @ x)
    return float(x @ y / denom) if denom > 0 else float("nan")


def mle(X):
    D = _dists(X)
    n = len(D)
    k = min(10, n - 2)
    knn = np.sort(D, axis=1)[:, :k]
    tk = knn[:, -1:]
    ratios = np.log(np.maximum(tk / np.maximum(knn[:, :-1], 1e-12), 1e-12))
    inv = ratios.mean(axis=1)
    m = 1.0 / np.maximum(inv, 1e-12)
    return float(m.mean())
