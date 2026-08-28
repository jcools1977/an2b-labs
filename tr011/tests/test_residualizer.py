#!/usr/bin/env python3
"""D5 residualizer bite-proof, written in Phase 0, red until Phase 4.

Two synthetic corpora, seeded and generated here:
- pure-length: group difference injected only through sentence-length
  statistics; after residualization every feature's |delta| must
  collapse below 0.1.
- orthogonal-entropy: a feature signal injected independently of
  length; after residualization deltas must retain >= 80% of their
  pre-residualization magnitude.

Fails red (import error) until analysis/residualize.py exists; then it
certifies the KILL instrument before any real data is analyzed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

SEED = 47
N_PER_GROUP = 60
FEATURES = ["mean", "variance", "acl", "lowfreq", "spike_rate", "boundary_delta"]


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return (gt - lt) / (len(a) * len(b))


def synth(kind):
    """Returns (features[n,6], length_stats[n,3], labels[n])."""
    rng = np.random.default_rng(SEED if kind == "length" else SEED + 1)
    n = 2 * N_PER_GROUP
    labels = np.array([0] * N_PER_GROUP + [1] * N_PER_GROUP)
    length = rng.normal(0, 1, (n, 3))
    feats = rng.normal(0, 1, (n, 6))
    if kind == "length":
        # group moves ONLY through length; features load on length stats
        length[labels == 1] += 1.5
        feats += length @ rng.normal(0.6, 0.1, (3, 6))
    else:
        # feature signal orthogonal to length: inject into two features
        feats[labels == 1, 0] += 1.2
        feats[labels == 1, 2] += 1.0
    return feats, length, labels


def deltas(feats, labels):
    return np.array([
        cliffs_delta(feats[labels == 1, j], feats[labels == 0, j])
        for j in range(feats.shape[1])
    ])


def main():
    try:
        from analysis.residualize import residualize
    except ImportError:
        print("RED: analysis/residualize.py does not exist yet (D5 bite-proof waiting)")
        return 1

    bad = 0

    feats, length, labels = synth("length")
    resid = residualize(feats, length)
    d = np.abs(deltas(resid, labels))
    if d.max() < 0.1:
        print(f"ok: planted pure-length signal collapses (max |delta| {d.max():.3f})")
    else:
        print(f"BROKEN: length signal survives residualization (max |delta| {d.max():.3f})")
        bad = 1

    feats, length, labels = synth("entropy")
    before = deltas(feats, labels)
    resid = residualize(feats, length)
    after = deltas(resid, labels)
    kept = [abs(after[j]) >= 0.8 * abs(before[j]) for j in (0, 2)]
    if all(kept):
        print(f"ok: planted orthogonal signal survives "
              f"({after[0]:.3f}/{before[0]:.3f}, {after[2]:.3f}/{before[2]:.3f})")
    else:
        print("BROKEN: residualizer over-corrects; orthogonal signal lost")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
