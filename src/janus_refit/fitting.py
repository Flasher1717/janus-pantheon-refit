"""Chi-square fits for the three models, sharing one MarginalizedChi2 pipeline.

Each shape parameter is minimized with scipy bounded scalar minimization; the
additive offset is already marginalized analytically inside MarginalizedChi2 and is
counted as one fitted parameter in n_params. The 1-sigma uncertainty on the shape
parameter is the local-curvature (Hessian) estimate sigma = sqrt(2 / chi2''),
with chi2'' from a central second difference at the minimum — a placeholder until
the M8 MCMC posteriors.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize_scalar

from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu, janus_q0_min, lcdm_mu_fast, milne_mu

OMEGA_M_BOUNDS = (0.01, 1.0)
JANUS_EDGE_MARGIN = 1e-6
"""Relative margin keeping the optimizer strictly inside the open Janus domain."""

LCDM_CHI2_REFERENCE = 1387.10
"""Published best-fit flat-LCDM chi2 for this exact configuration — Pantheon+ full
STAT+SYS covariance, zHD > 0.01, Cepheid calibrators excluded (N = 1580), additive
offset profiled: Keeley, Shafieloo & L'Huillier 2024, Universe 10, 439
(arXiv:2212.07917). Sanity gate recalibrated to this value from the SPEC's a-priori
[1400, 1500] band with Teo's explicit GO (2026-06-10), pre-registered before any
Janus or Milne chi2 was inspected; see RESULTS.md section 6."""

LCDM_CHI2_TOLERANCE = 1.0
"""Half-width of the sanity gate around LCDM_CHI2_REFERENCE."""


@dataclass(frozen=True)
class FitResult:
    model: str
    params: dict[str, float]
    sigmas: dict[str, float]
    chi2: float
    n_points: int
    n_params: int

    @property
    def dof(self) -> int:
        return self.n_points - self.n_params

    @property
    def chi2_dof(self) -> float:
        return self.chi2 / self.dof


def _curvature_sigma(objective: Callable[[float], float], best: float, step: float) -> float:
    second = (objective(best + step) - 2.0 * objective(best) + objective(best - step)) / step**2
    if second <= 0.0:
        return float("nan")
    return float(np.sqrt(2.0 / second))


def _minimize_with_sigma(
    objective: Callable[[float], float],
    bounds: tuple[float, float],
    sigma_step: float,
) -> tuple[float, float, float]:
    result = minimize_scalar(objective, bounds=bounds, method="bounded", options={"xatol": 1e-8})
    best = float(result.x)
    return best, _curvature_sigma(objective, best, sigma_step), float(result.fun)


def fit_lcdm(chi2: MarginalizedChi2, h0: float = 70.0) -> FitResult:
    def objective(omega_m: float) -> float:
        return chi2(lcdm_mu_fast(chi2.z, omega_m, h0))

    best, sigma, chi2_min = _minimize_with_sigma(objective, OMEGA_M_BOUNDS, sigma_step=1e-3)
    return FitResult(
        model="FlatLCDM",
        params={"omega_m": best},
        sigmas={"omega_m": sigma},
        chi2=chi2_min,
        n_points=chi2.n_points,
        n_params=2,
    )


def fit_janus(chi2: MarginalizedChi2, h0: float = 70.0) -> FitResult:
    q0_min = janus_q0_min(float(chi2.z.max()))
    bounds = (q0_min * (1.0 - JANUS_EDGE_MARGIN), q0_min * JANUS_EDGE_MARGIN)

    def objective(q0: float) -> float:
        return chi2(janus_mu(chi2.z, q0, h0))

    best, sigma, chi2_min = _minimize_with_sigma(objective, bounds, sigma_step=1e-4)
    return FitResult(
        model="Janus",
        params={"q0": best},
        sigmas={"q0": sigma},
        chi2=chi2_min,
        n_points=chi2.n_points,
        n_params=2,
    )


def fit_milne(chi2: MarginalizedChi2, h0: float = 70.0) -> FitResult:
    return FitResult(
        model="Milne",
        params={},
        sigmas={},
        chi2=chi2(milne_mu(chi2.z, h0)),
        n_points=chi2.n_points,
        n_params=1,
    )
