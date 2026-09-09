#!/usr/bin/env python3
"""Certification exam for the regime test. World S (step): accuracy
0.35 below S=8 and 0.65 at and above, n=200 per point, 18 points: the
margin must be >= 10 and the breakpoint must be S=8. World L
(logistic, smooth): the margin must be < 10 (the red side: a test
that finds regimes in smooth curves is worthless). World F (flat):
margin < 10. Exit nonzero on any leg."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.regime import S_GRID, regime_test  # noqa: E402


def world(kind, seed):
    rng = np.random.default_rng(seed)
    pts = []
    for S in S_GRID:
        for F in (1, 2, 4):
            x = math.log2(S)
            if kind == "step":
                p = 0.35 if S < 8 else 0.65
            elif kind == "logistic":
                p = 1 / (1 + math.exp(-(x - 2.5) * 0.9)) * 0.5 + 0.25
            else:
                p = 0.45
            pts.append({"S": S, "F": F, "k": int(rng.binomial(200, p)), "n": 200})
    return pts


def main():
    bad = 0
    for kind, want_regime, bp in (("step", True, 8), ("logistic", False, None), ("flat", False, None)):
        margins = []
        for seed in range(5):
            r = regime_test(world(kind, seed))
            margins.append(r["aic_margin"])
            if want_regime and r["breakpoint_S"] != bp:
                print(f"  FAIL {kind} seed {seed}: breakpoint {r['breakpoint_S']} != {bp}")
                bad += 1
        ok = all(m >= 10 for m in margins) if want_regime else all(m < 10 for m in margins)
        print(f"  {'ok ' if ok else 'FAIL'} {kind:8} margins {[round(m, 1) for m in margins]} "
              f"({'must all be >= 10' if want_regime else 'must all be < 10'})")
        bad += 0 if ok else 1
    print(f"regime exam: {'CERTIFIED' if bad == 0 else str(bad) + ' legs failing'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
