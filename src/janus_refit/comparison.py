"""Model-comparison statistics (M9): AIC and BIC.

AIC = chi2 + 2k (Akaike 1974); BIC = chi2 + k ln n (Schwarz 1978), with k the
number of fitted parameters (counting the analytically profiled offset) and n the
number of data points. Applied to the frozen M7 chi-square values
(janus_refit.reference). Lower is better; only differences between models fitted
to the same data and covariance are meaningful (RESULTS.md section 8).
"""

from math import log


def aic(chi2: float, n_params: int) -> float:
    return chi2 + 2.0 * n_params


def bic(chi2: float, n_params: int, n_points: int) -> float:
    return chi2 + n_params * log(n_points)
