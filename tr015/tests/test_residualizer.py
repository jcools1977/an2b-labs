#!/usr/bin/env python3
"""D6 residualizer bite-proof, red until analysis/residualize exists.

Synthetic chunks: embeddings 64-dim, 8 authors x 40 chunks.
- topic exam: class signal injected ONLY through topic factors; after
  residualization, nearest-centroid attribution must fall within 5
  points of chance.
- voice exam: class signal orthogonal to topic factors; attribution
  must retain >= 80% of its pre-residualization margin over chance.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np

SEED, AUTHORS, CHUNKS, DIM, TOPICS = 53, 8, 40, 64, 5


def attribution(X, y):
    # leave-half-out nearest centroid, deterministic
    n = len(y)
    tr = np.arange(n) % 2 == 0
    cents = {a: X[tr & (y == a)].mean(0) for a in np.unique(y)}
    pred = [min(cents, key=lambda a: np.linalg.norm(x - cents[a]))
            for x in X[~tr]]
    return float((np.array(pred) == y[~tr]).mean())


def synth(kind):
    rng = np.random.default_rng(SEED if kind == "topic" else SEED + 1)
    y = np.repeat(np.arange(AUTHORS), CHUNKS)
    n = len(y)
    T = rng.dirichlet(np.ones(TOPICS), n)  # topic factors
    X = rng.normal(0, 1, (n, DIM))
    load = rng.normal(0.8, 0.1, (TOPICS, DIM))
    X += T @ load  # topics always leak into embeddings
    if kind == "topic":
        for a in range(AUTHORS):
            T[y == a] += rng.dirichlet(np.ones(TOPICS)) * 1.5  # class via topics only
        X = rng.normal(0, 1, (n, DIM)) + T @ load
    else:
        V = rng.normal(0, 1, (AUTHORS, DIM))
        X += V[y] * 1.2  # class signal orthogonal to topics
    return X, T, y


def main():
    try:
        from analysis.residualize import residualize
    except ImportError:
        print("RED: analysis/residualize does not exist yet (D6 waiting)")
        return 1
    bad = 0
    chance = 1 / AUTHORS

    X, T, y = synth("topic")
    acc = attribution(residualize(X, T), y)
    if acc <= chance + 0.05:
        print(f"ok: planted topic signal collapses ({acc:.3f} vs chance {chance:.3f})")
    else:
        print(f"BROKEN: topic signal survives residualization ({acc:.3f})")
        bad = 1

    X, T, y = synth("voice")
    before = attribution(X, y)
    after = attribution(residualize(X, T), y)
    if (after - chance) >= 0.8 * (before - chance):
        print(f"ok: planted voice signal survives ({after:.3f} of {before:.3f})")
    else:
        print(f"BROKEN: residualizer over-corrects ({after:.3f} of {before:.3f})")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
