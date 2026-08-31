"""Topic residualization (D5), certified by the D6 bite-proof before
any real embedding may pass through it.

Ordinary least squares with intercept: each embedding dimension is
regressed on the LDA topic-proportion matrix across chunks; the
returned matrix is the residuals. Over-correction and under-correction
are both failure modes the D6 exam rejects (signal planted only through
topics must collapse to within 5 points of chance; signal orthogonal to
topics must survive at >= 80% of its margin).
"""
import numpy as np


def residualize(embeddings, topic_props):
    E = np.asarray(embeddings, dtype=float)
    T = np.asarray(topic_props, dtype=float)
    X = np.hstack([np.ones((len(T), 1)), T])
    beta, *_ = np.linalg.lstsq(X, E, rcond=None)
    return E - X @ beta
