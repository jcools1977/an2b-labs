"""Curvature proxies (D4), certified alongside the LID estimators.

geodesic_chordal_ratio: mean ratio of k-NN-graph shortest-path
distance to straight-line distance over all connected point pairs
(k = min(8, n-1)); 1.0 on a flat cloud, above 1.0 when the manifold
bends. Restricted to the largest connected component.
pca_decay: reported-only residual spectrum decay rate (log-linear
slope of the sorted eigenvalue tail).
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path
from scipy.spatial.distance import pdist, squareform


def geodesic_chordal_ratio(X):
    X = np.asarray(X, dtype=float)
    n = len(X)
    k = min(8, n - 1)
    D = squareform(pdist(X))
    idx = np.argsort(D, axis=1)[:, 1:k + 1]
    rows = np.repeat(np.arange(n), k)
    cols = idx.ravel()
    graph = csr_matrix((D[rows, cols], (rows, cols)), shape=(n, n))
    ncomp, labels = connected_components(graph, directed=False)
    if ncomp > 1:
        main = np.argmax(np.bincount(labels))
        keep = np.where(labels == main)[0]
        D = D[np.ix_(keep, keep)]
        n = len(keep)
        k = min(8, n - 1)
        idx = np.argsort(D, axis=1)[:, 1:k + 1]
        rows = np.repeat(np.arange(n), k)
        cols = idx.ravel()
        graph = csr_matrix((D[rows, cols], (rows, cols)), shape=(n, n))
    G = shortest_path(graph, method="D", directed=False)
    iu = np.triu_indices(n, 1)
    geo, cho = G[iu], D[iu]
    ok = np.isfinite(geo) & (cho > 0)
    return float(np.mean(geo[ok] / cho[ok]))


def pca_decay(X):
    X = np.asarray(X, dtype=float)
    Xc = X - X.mean(0)
    ev = np.linalg.svd(Xc, compute_uv=False) ** 2
    ev = ev[ev > 1e-12]
    tail = ev[1:] if len(ev) > 1 else ev
    y = np.log(tail)
    x = np.arange(len(y))
    return float(np.polyfit(x, y, 1)[0]) if len(y) > 1 else 0.0
