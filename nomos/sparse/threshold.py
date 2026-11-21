"""
NOMOS Threshold Selection Framework (AIC / BIC / Cross-Validation)
Agent D03 & I05
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np


def compute_information_criteria(
    Theta: np.ndarray,
    X_dot: np.ndarray,
    Xi: np.ndarray,
) -> Dict[str, float]:
    """
    Compute AIC and BIC for candidate coefficient matrix Xi:
        RSS = ||X_dot - Theta * Xi||_F^2
        k = ||Xi||_0
        AIC = M * ln(RSS / M) + 2 * k
        BIC = M * ln(RSS / M) + k * ln(M)
    """
    M, n = X_dot.shape
    residual = X_dot - Theta @ Xi
    rss = float(np.sum(residual ** 2))
    k = int(np.count_nonzero(Xi))

    if rss < 1e-12:
        rss = 1e-12

    log_term = M * np.log(rss / M)
    aic = float(log_term + 2 * k)
    bic = float(log_term + k * np.log(M))

    return {
        "rss": rss,
        "active_terms": k,
        "aic": aic,
        "bic": bic,
    }
