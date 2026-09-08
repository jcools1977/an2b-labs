"""TR-003r retrieval and the protocol's metrics, computed from two
matrices in a common frame: store S (m, r) and queries Q (n, r).
Cosine similarity; top-10 kept for ranking stability.
"""
import numpy as np

from analysis.anchors import unit

TOPK = 10


def topk(Q, S, k=TOPK):
    scores = unit(Q) @ unit(S).T
    idx = np.argpartition(-scores, k, axis=1)[:, :k]
    sc = np.take_along_axis(scores, idx, axis=1)
    order = np.argsort(-sc, axis=1)
    return np.take_along_axis(idx, order, axis=1), np.take_along_axis(sc, order, axis=1)


def metrics(top_idx, top_sc, target_idx, store_work, target_work,
            native_top_idx=None, native_median_margin=None):
    """All protocol metrics for one condition on one query set.

    target_idx: (n,) store index of the correct memory.
    store_work: (m,) work id per store chunk; target_work: (n,) work per query.
    native_*: the C1 result in the query model for the same queries.
    """
    n = len(target_idx)
    hit1 = top_idx[:, 0] == target_idx
    hit5 = (top_idx[:, :5] == target_idx[:, None]).any(1)
    ranks = np.where(top_idx == target_idx[:, None])
    rr = np.zeros(n)
    rr[ranks[0]] = 1.0 / (ranks[1] + 1)
    work1 = store_work[top_idx[:, 0]]
    prov_work = work1 == target_work
    margin = top_sc[:, 0] - top_sc[:, 1]
    out = {"n": int(n), "r1": float(hit1.mean()), "r5": float(hit5.mean()),
           "mrr": float(rr.mean()), "provenance_work": float(prov_work.mean()),
           "provenance_chunk": float(hit1.mean()),
           "median_margin": float(np.median(margin))}
    ref_margin = out["median_margin"] if native_median_margin is None else native_median_margin
    cw = (~hit1) & (~prov_work) & (margin > ref_margin)
    out["confident_wrong"] = float(cw.mean())
    if native_top_idx is not None:
        inter = np.array([len(set(a) & set(b)) for a, b in zip(top_idx, native_top_idx)])
        union = np.array([len(set(a) | set(b)) for a, b in zip(top_idx, native_top_idx)])
        out["jaccard10"] = float((inter / union).mean())
    return out
