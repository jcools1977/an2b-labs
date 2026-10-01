"""TR-013 indicators (D5) over a trailing window of W turns on the
per-turn embedding series E (n, 384) and the turn texts:
  variance: trace of the window covariance (full space)
  lag1_autocorr: mean over dimensions of the lag-1 autocorrelation
  distinct2: distinct-2 token diversity of the window's text
plus the top-8 PCA companions of the first two (fit on control runs
only, passed in). Slopes over the window via least squares."""
import re

import numpy as np

W = 10
PCS = 8


def distinct2(texts):
    toks = [w for t in texts for w in re.findall(r"[a-z0-9']+", t.lower())]
    if len(toks) < 2:
        return 0.0
    bigrams = list(zip(toks, toks[1:]))
    return len(set(bigrams)) / len(bigrams)


def lag1(X):
    """Mean over columns of lag-1 autocorrelation of a (w, d) window."""
    Xc = X - X.mean(0)
    num = (Xc[:-1] * Xc[1:]).sum(0)
    den = (Xc * Xc).sum(0) + 1e-12
    return float((num / den).mean())


def indicator_series(E, texts, P=None):
    """Per-turn indicator values at turns t >= W (1-based turn index t).
    Returns dict of arrays aligned to turns W..n."""
    n = len(E)
    out = {"turn": [], "variance": [], "lag1_autocorr": [], "distinct2": [], "variance_pc": [], "lag1_pc": []}
    for t in range(W, n + 1):
        X = E[t - W:t]
        out["turn"].append(t)
        out["variance"].append(float(np.trace(np.cov(X.T))))
        out["lag1_autocorr"].append(lag1(X))
        out["distinct2"].append(distinct2(texts[t - W:t]))
        if P is not None:
            Z = X @ P.T
            out["variance_pc"].append(float(np.trace(np.cov(Z.T))))
            out["lag1_pc"].append(lag1(Z))
    return {k: np.array(v) for k, v in out.items()}


def slope(series, w=W):
    """Least-squares slope of the trailing w values at each position (nan where unavailable)."""
    s = np.full(len(series), np.nan)
    x = np.arange(w) - (w - 1) / 2
    for i in range(w - 1, len(series)):
        y = series[i - w + 1:i + 1]
        s[i] = float((x * (y - y.mean())).sum() / (x * x).sum())
    return s


def fit_pca(E_controls, k=PCS):
    mu = E_controls.mean(0)
    _, _, Vt = np.linalg.svd(E_controls - mu, full_matrices=False)
    return Vt[:k]
