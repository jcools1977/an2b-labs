"""Covariate residualization for paired differences (D7, D17),
certified by the bite-proof exam before any real number passes
through it.

The D17 commitment: covariates with a meaningful zero enter
uncentered (their slope contribution, mean included, is removable
confound); covariates without one enter centered (only covariation is
removable). The grand-mean effect independent of covariates is kept;
a full-OLS subtraction with intercept would eat it, and the exam's
first leg rejects that implementation.
"""
import numpy as np


def residualize_diffs(diffs, covariates, meaningful_zero):
    y = np.asarray(diffs, dtype=float)
    Z = np.asarray(covariates, dtype=float).copy()
    mz = np.asarray(meaningful_zero, dtype=bool)
    Z[:, ~mz] -= Z[:, ~mz].mean(axis=0)
    X = np.column_stack([np.ones(len(y)), Z])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - Z @ beta[1:]
