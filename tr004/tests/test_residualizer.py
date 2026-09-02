#!/usr/bin/env python3
"""D7/D17 residualizer bite-proof, red until analysis/residualize
exists and encodes the identifiability commitment.

Covariate 0 is frequency-like (no meaningful zero, centered class);
covariate 1 is length-difference-like (meaningful zero, uncentered
class). The exam:
- intercept trap: a true constant effect independent of covariates
  must retain >= 80% of its Cliff's delta (a full-OLS subtraction
  fails this).
- meaningful-zero confound: effect generated purely as slope times
  covariate 1 (nonzero mean) must collapse to |delta| <= 0.05.
- centered-covariate decorrelation: after residualization, the
  Spearman correlation with covariate 0 must be |rho| <= 0.1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import spearmanr

SEED, N = 53, 2000


def cliffs(x):
    return float((np.sum(x > 0) - np.sum(x < 0)) / len(x))


def main():
    try:
        from analysis.residualize import residualize_diffs
    except ImportError:
        print("RED: analysis/residualize does not exist yet (D7 waiting)")
        return 1
    rng = np.random.default_rng(SEED)
    bad = 0
    Z = np.column_stack([rng.normal(2, 0.8, N),    # freq-like, centered
                         rng.normal(1.5, 3, N)])   # lendiff-like, zero real
    MEANINGFUL_ZERO = [False, True]

    effect = 0.5 + rng.normal(0, 0.4, N)
    before = cliffs(effect)
    after = cliffs(residualize_diffs(effect, Z, MEANINGFUL_ZERO))
    if after >= 0.8 * before:
        print(f"ok: true effect survives ({after:.3f} of {before:.3f})")
    else:
        print(f"BROKEN: residualizer eats the effect "
              f"({after:.3f} of {before:.3f}); the intercept trap")
        bad = 1

    confound = 0.25 * Z[:, 1] + rng.normal(0, 0.2, N)
    d = cliffs(residualize_diffs(confound, Z, MEANINGFUL_ZERO))
    if abs(d) <= 0.05:
        print(f"ok: meaningful-zero confound collapses (delta {d:+.3f})")
    else:
        print(f"BROKEN: confound survives residualization (delta {d:+.3f})")
        bad = 1

    fdriven = 0.6 * Z[:, 0] + rng.normal(0, 0.2, N)
    r = residualize_diffs(fdriven, Z, MEANINGFUL_ZERO)
    rho = abs(spearmanr(r, Z[:, 0]).statistic)
    if rho <= 0.1:
        print(f"ok: centered covariate decorrelated (|rho| {rho:.3f})")
    else:
        print(f"BROKEN: residual still tracks the centered covariate "
              f"(|rho| {rho:.3f})")
        bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
