"""TR-006 regime test, operationalized in DECISIONS D8 before data.

Data: points (S, F, k, n): k correct of n at capacity S, frequency F.
Pooled over F within a family (18 points). x = log2 S.
Smooth monotone model (2 params): p = sigmoid(a + b x), b >= 0.
Regime (step) model (3 params): p = sigmoid(c) for x < x*, sigmoid(d)
for x >= x*, with d >= c ("performance jumps"), x* at a grid midpoint
between consecutive S values; the best x* is chosen and counted as a
parameter. AIC = 2k - 2 logL, binomial likelihood.
margin = AIC_smooth - AIC_regime; PASS clause needs margin >= 10.
"""
import math

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, gammaln

S_GRID = [1, 2, 4, 8, 16, 32]


def _ll(p, k, n):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(np.sum(gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)
                        + k * np.log(p) + (n - k) * np.log(1 - p)))


def fit_smooth(x, k, n):
    def nll(th):
        a, b = th
        return -_ll(expit(a + b * x), k, n)
    best = None
    for a0 in (-1.0, 0.0, 1.0):
        for b0 in (0.0, 0.3, 1.0):
            r = minimize(nll, [a0, b0], bounds=[(-10, 10), (0, 10)], method="L-BFGS-B")
            if best is None or r.fun < best.fun:
                best = r
    ll = -best.fun
    return {"params": {"a": float(best.x[0]), "b": float(best.x[1])}, "loglik": ll, "aic": 2 * 2 - 2 * ll}


def fit_regime(x, k, n):
    best = None
    xs = sorted(set(x.tolist()))
    for i in range(1, len(xs)):
        xstar = 0.5 * (xs[i - 1] + xs[i])
        lo, hi = x < xstar, x >= xstar
        pl = (k[lo].sum() + 0.5) / (n[lo].sum() + 1.0)
        ph = (k[hi].sum() + 0.5) / (n[hi].sum() + 1.0)
        if ph < pl:  # d >= c: a jump, not a drop
            ph = pl = (k.sum() + 0.5) / (n.sum() + 1.0)
        ll = _ll(np.where(lo, pl, ph), k, n)
        if best is None or ll > best["loglik"]:
            best = {"params": {"p_low": float(pl), "p_high": float(ph), "x_star": xstar},
                    "breakpoint_S": int(2 ** xs[i]), "loglik": ll, "aic": 2 * 3 - 2 * ll}
    return best


def regime_test(points):
    """points: list of dicts with S, F, k, n."""
    x = np.array([math.log2(p["S"]) for p in points], float)
    k = np.array([p["k"] for p in points], float)
    n = np.array([p["n"] for p in points], float)
    sm, rg = fit_smooth(x, k, n), fit_regime(x, k, n)
    return {"aic_smooth": sm["aic"], "aic_regime": rg["aic"], "aic_margin": sm["aic"] - rg["aic"],
            "breakpoint_S": rg["breakpoint_S"], "smooth": sm, "regime": rg, "n_points": len(points)}
