#!/usr/bin/env python3
"""Certification exam for the anchor library (before any real duty).

World R (recoverable): space B is an exact rotation of space A plus
small noise. C3 and C4 must retrieve near-perfectly; the mismatched-
anchor and random-projection arms must sit at chance.
World N (no structure): space B is independent of A. C3 must sit at
chance. This is the exam's RED side: a library that retrieves here is
manufacturing alignment.
Exit nonzero on any leg failing.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.anchors import (naive_map, procrustes_map, random_projection_pair,  # noqa: E402
                              relative, unit)
from analysis.retrieval import metrics, topk  # noqa: E402

N_STORE, N_Q, D, K = 3000, 300, 64, 256
CHANCE5 = 5 / N_STORE


def world(seed, structured):
    rng = np.random.default_rng(seed)
    # clustered data so cosine geometry is nontrivial
    centers = rng.standard_normal((30, D)) * 3
    lab = rng.integers(0, 30, N_STORE + N_Q + 2 * K)
    A = centers[lab] + rng.standard_normal((len(lab), D))
    Rm, _ = np.linalg.qr(rng.standard_normal((D, D)))
    if structured:
        B = A @ Rm + 0.15 * rng.standard_normal(A.shape)
    else:
        B = rng.standard_normal(A.shape)
    S_A, S_B = A[:N_STORE], B[:N_STORE]
    # queries are noisy copies of the first N_Q STORE points (their targets)
    q = np.arange(N_Q)
    Q_A = A[q] + 0.1 * rng.standard_normal((N_Q, D))
    Q_B = B[q] + 0.1 * rng.standard_normal((N_Q, D))
    anc = np.arange(N_STORE + N_Q, N_STORE + N_Q + K)
    anc2 = anc + K
    return dict(S_A=S_A, S_B=S_B, Q_A=Q_A, Q_B=Q_B, targets=np.arange(N_Q),
                anc_A=A[anc], anc_B=B[anc], anc_B_mismatch=B[anc2],
                works=np.arange(N_STORE) // 100)


def run(w, arm):
    if arm == "C1":
        S, Q = w["S_A"], w["Q_A"]
    elif arm == "C3":
        S, Q = relative(w["S_A"], w["anc_A"]), relative(w["Q_B"], w["anc_B"])
    elif arm == "C4":
        f_src, f_tgt = procrustes_map(w["anc_A"], w["anc_B"])
        S, Q = f_src(w["S_A"]), f_tgt(w["Q_B"])
    elif arm == "mismatched":
        S, Q = relative(w["S_A"], w["anc_A"]), relative(w["Q_B"], w["anc_B_mismatch"])
    elif arm == "random_projection":
        Ra, Rb = random_projection_pair(D, D, K, 7)
        S, Q = w["S_A"] @ Ra, w["Q_B"] @ Rb
    elif arm == "C2":
        S, Q = naive_map(w["S_A"], D, 7), w["Q_B"]
    idx, sc = topk(Q, S)
    return metrics(idx, sc, w["targets"], w["works"], w["works"][w["targets"]])["r5"]


def main():
    bad = 0

    def leg(desc, ok, val):
        nonlocal bad
        print(f"  {'ok ' if ok else 'FAIL'} {desc}: r5={val:.3f}")
        bad += 0 if ok else 1
    print("World R (recoverable)")
    w = world(41, True)
    v = run(w, "C1"); leg("world sanity: native retrieval in A (>= 0.95)", v >= 0.95, v)
    v = run(w, "C3"); leg("C3 relative reps recover retrieval (>= 0.95)", v >= 0.95, v)
    v = run(w, "C4"); leg("C4 Procrustes ceiling recovers retrieval (>= 0.95)", v >= 0.95, v)
    v = run(w, "mismatched"); leg("mismatched anchors collapse to chance (<= chance+0.02)", v <= CHANCE5 + 0.02, v)
    v = run(w, "random_projection"); leg("random projections at chance (<= chance+0.02)", v <= CHANCE5 + 0.02, v)
    v = run(w, "C2"); leg("naive raw vectors across a rotation at chance (<= chance+0.02)", v <= CHANCE5 + 0.02, v)
    print("World N (no structure), the red side")
    w = world(43, False)
    v = run(w, "C1"); leg("world sanity: native retrieval in A (>= 0.95)", v >= 0.95, v)
    v = run(w, "C3"); leg("C3 at chance when spaces are unrelated (<= chance+0.02)", v <= CHANCE5 + 0.02, v)
    v = run(w, "C4"); leg("C4 at chance when spaces are unrelated (<= chance+0.05)", v <= CHANCE5 + 0.05, v)
    print(f"anchor exam: {'CERTIFIED' if bad == 0 else str(bad) + ' legs failing'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
