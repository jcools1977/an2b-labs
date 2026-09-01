#!/usr/bin/env python3
"""D5 estimator certification exam, red until analysis/lid and
analysis/curvature exist and pass.

- Uniform d-balls (d in {2, 5, 10}) embedded in 384 dims via a random
  orthogonal frame: both estimators within 20% at n=500.
- At n=40 (our cloud scale) both must preserve ORDER (d=2 < d=10).
- Both estimators must agree in direction on a d=5 vs d=9 pair.
- Geodesic-chordal proxy must separate a 2-sphere from a flat 2-disk
  of matched n, and read within 5% of 1.0 on the disk.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np

SEED, AMBIENT = 53, 384


def ball(rng, d, n):
    x = rng.normal(0, 1, (n, d))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    r = rng.uniform(0, 1, (n, 1)) ** (1 / d)
    frame = np.linalg.qr(rng.normal(0, 1, (AMBIENT, d)))[0]
    return (x * r) @ frame.T


def sphere2(rng, n):
    x = rng.normal(0, 1, (n, 3))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    frame = np.linalg.qr(rng.normal(0, 1, (AMBIENT, 3)))[0]
    return x @ frame.T


def disk2(rng, n):
    return ball(rng, 2, n)


def main():
    try:
        from analysis.lid import twonn, mle
        from analysis.curvature import geodesic_chordal_ratio
    except ImportError:
        print("RED: analysis/lid and analysis/curvature do not exist yet "
              "(D5 waiting)")
        return 1
    rng = np.random.default_rng(SEED)
    bad = 0

    for d in (2, 5, 10):
        X = ball(rng, d, 500)
        for name, est in (("twonn", twonn), ("mle", mle)):
            got = est(X)
            if abs(got - d) / d <= 0.20:
                print(f"ok: {name} recovers d={d} at n=500 ({got:.2f})")
            else:
                print(f"BROKEN: {name} reads {got:.2f} for d={d} at n=500")
                bad = 1

    lo2, hi10 = {}, {}
    for name, est in (("twonn", twonn), ("mle", mle)):
        lo2[name] = est(ball(rng, 2, 40))
        hi10[name] = est(ball(rng, 10, 40))
        if lo2[name] < hi10[name]:
            print(f"ok: {name} preserves order at n=40 "
                  f"({lo2[name]:.2f} < {hi10[name]:.2f})")
        else:
            print(f"BROKEN: {name} order violated at n=40 "
                  f"({lo2[name]:.2f} !< {hi10[name]:.2f})")
            bad = 1

    d5 = {n: e(ball(rng, 5, 200)) for n, e in
          (("twonn", twonn), ("mle", mle))}
    d9 = {n: e(ball(rng, 9, 200)) for n, e in
          (("twonn", twonn), ("mle", mle))}
    if all(d9[n] > d5[n] for n in d5):
        print("ok: estimators agree in direction on d=5 vs d=9")
    else:
        print(f"BROKEN: direction disagreement (d5={d5}, d9={d9})")
        bad = 1

    r_sphere = geodesic_chordal_ratio(sphere2(rng, 300))
    r_disk = geodesic_chordal_ratio(disk2(rng, 300))
    if r_sphere > r_disk:
        print(f"ok: proxy separates sphere from disk "
              f"({r_sphere:.3f} > {r_disk:.3f})")
    else:
        print(f"BROKEN: proxy fails sphere vs disk "
              f"({r_sphere:.3f} !> {r_disk:.3f})")
        bad = 1
    if abs(r_disk - 1.0) <= 0.05:
        print(f"ok: proxy reads near-flat on the disk ({r_disk:.3f})")
    else:
        print(f"BROKEN: proxy reads {r_disk:.3f} on a flat disk")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
