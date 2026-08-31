"""Length residualization (D4), certified by the D5 bite-proof before
any real data may pass through it.

Ordinary least squares with intercept: each feature column is regressed
on the sentence-length statistics matrix across documents; the returned
matrix is the residuals. Over-correction and under-correction are both
failure modes the D5 exam rejects (planted pure-length signal must
collapse; planted orthogonal signal must survive at >= 80% magnitude).
"""
import numpy as np


def residualize(features, length_stats):
    F = np.asarray(features, dtype=float)
    L = np.asarray(length_stats, dtype=float)
    X = np.hstack([np.ones((len(L), 1)), L])
    beta, *_ = np.linalg.lstsq(X, F, rcond=None)
    return F - X @ beta
