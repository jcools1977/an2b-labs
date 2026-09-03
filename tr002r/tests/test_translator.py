#!/usr/bin/env python3
"""Translator certification exam (D11), red until analysis/translator
exists. Two legs, both on synthetic spaces where truth is known:

- recoverable-structure leg: space B is an orthogonal transform of
  space A plus small noise; trained UNPAIRED (disjoint halves), the
  D3 procedure must reach top-1 >= 0.9 on a 500-item held-out
  gallery. Failure means the implementation is broken, because this
  is the easiest world the method can face.
- no-structure leg: space B is an independent random cloud with no
  shared geometry; the procedure must NOT beat 10x chance (0.02 at
  n=500). Success here would mean the pipeline manufactures
  alignment, the exact disease the shuffled-target control exists to
  catch in production.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np

SEED, DIM, N_TRAIN, N_EVAL = 53, 96, 3000, 500


def make_base(rng, n):
    # Mixture world (D11 third addendum): the method class anchors on
    # cluster structure ("recurring themes"); the fair easy world has
    # 24 latent clusters, skewed within-cluster spread, distinct
    # cluster geometry. Centers drawn once from a fixed generator so
    # both halves and eval share the same mixture.
    crng = np.random.default_rng(977)
    centers = crng.normal(0, 2.5, (24, 12))
    load = crng.normal(0, 1, (12, DIM))
    z = rng.integers(0, 24, n)
    Z = centers[z] + 0.4 * (rng.gamma(2.0, 1.0, (n, 12)) - 2.0)
    return Z @ load + 0.1 * rng.normal(0, 1, (n, DIM))


def main():
    try:
        from analysis.translator import (apply_translator, target_space,
                                         train_translator)
    except ImportError:
        print("RED: analysis/translator does not exist yet (D11 waiting)")
        return 1
    rng = np.random.default_rng(SEED)
    bad = 0

    base_train = make_base(rng, 2 * N_TRAIN)
    base_eval = make_base(rng, N_EVAL)
    Q = np.linalg.qr(rng.normal(0, 1, (DIM, DIM)))[0]

    A_half = base_train[:N_TRAIN]
    B_half = base_train[N_TRAIN:] @ Q + 0.02 * rng.normal(
        0, 1, (N_TRAIN, DIM))
    A_eval, B_eval = base_eval, base_eval @ Q

    T = train_translator(A_half, B_half, seed=41)
    pred = apply_translator(T, A_eval)
    gal = target_space(T, B_eval)
    sims = pred @ gal.T / (
        np.linalg.norm(pred, axis=1, keepdims=True) *
        np.linalg.norm(gal, axis=1, keepdims=True).T + 1e-12)
    top1 = float((np.argmax(sims, axis=1) == np.arange(N_EVAL)).mean())
    if top1 >= 0.9:
        print(f"ok: recoverable structure recovered (top-1 {top1:.3f})")
    else:
        print(f"BROKEN: top-1 {top1:.3f} < 0.9 on the easiest world")
        bad = 1

    B_rand = make_base(np.random.default_rng(SEED + 7), N_TRAIN)
    B_rand_eval = make_base(np.random.default_rng(SEED + 8), N_EVAL)
    T2 = train_translator(A_half, B_rand, seed=41)
    pred2 = apply_translator(T2, A_eval)
    gal2 = target_space(T2, B_rand_eval)
    sims2 = pred2 @ gal2.T / (
        np.linalg.norm(pred2, axis=1, keepdims=True) *
        np.linalg.norm(gal2, axis=1, keepdims=True).T + 1e-12)
    top1_r = float((np.argmax(sims2, axis=1) == np.arange(N_EVAL)).mean())
    if top1_r <= 10 * (1 / N_EVAL):
        print(f"ok: no structure, no alignment manufactured "
              f"(top-1 {top1_r:.3f})")
    else:
        print(f"BROKEN: manufactures alignment from nothing "
              f"(top-1 {top1_r:.3f})")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
