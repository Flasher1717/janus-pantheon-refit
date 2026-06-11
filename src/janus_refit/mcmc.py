"""Posterior sampling for the shape parameters (M8).

The additive offset is profiled analytically inside MarginalizedChi2 (RESULTS.md
section 6.1), so each model's posterior is one-dimensional:
log L(theta) = -chi2_marg(theta) / 2 under a flat prior on the shape parameter.
Milne has no shape parameter: its posterior is the single point chi2 reported at M7
and is documented as such, with no sampling.

Pre-registered priors (M8 GO, recorded in RESULTS.md section 6.5 and committed
BEFORE the production run): LCDM omega_m in (0.01, 1.0) open; Janus q0 in
(janus_q0_min(z_max), 0.0) open — the upper bound 0 is the model's validity domain
(E < 0), not a tuning choice; posterior mass piling against it would itself be a
reportable result. log_prob returns -inf strictly outside the open interval BEFORE
evaluating the model (model validators raise outside their domain by design).

Pre-registered convergence criterion: n_steps > 50 * tau, with tau the integrated
autocorrelation time (Sokal estimator, emcee implementation). Burn-in = ceil(3 tau),
thinning = max(1, floor(tau / 2)) — the convention of the emcee documentation.
"""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil, floor

import numpy as np
from emcee import EnsembleSampler

from janus_refit._types import FloatArray
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu, janus_q0_min, lcdm_mu_fast

N_WALKERS = 32
N_STEPS = 4000
SEED_LCDM = 20260610
SEED_JANUS = 20260611
CONVERGENCE_FACTOR = 50.0
LCDM_PRIOR = (0.01, 1.0)
H0_FIDUCIAL = 70.0
"""Fixed for model evaluation only — fully degenerate with the profiled offset
(invariance tested at the likelihood level)."""

INIT_MARGIN = 1e-9
"""Relative inset of the walker initialization inside the open prior interval, so no
walker starts exactly on a boundary where log_prob is -inf. Initialization detail
only — the prior itself is unchanged."""


@dataclass(frozen=True)
class ChainSpec:
    """Identity of one sampled chain: model label, parameter name, fixed seed."""

    model: str
    param: str
    seed: int


LCDM_SPEC = ChainSpec(model="FlatLCDM", param="omega_m", seed=SEED_LCDM)
JANUS_SPEC = ChainSpec(model="Janus", param="q0", seed=SEED_JANUS)

SEED_JANUS_JLA = 20260612
JANUS_JLA_SPEC = ChainSpec(model="Janus", param="q0", seed=SEED_JANUS_JLA)
"""v1.1 pre-tag GO (Téo, 2026-06-10): express MCMC cross-check of the arm-B Janus
fit on JLA, same protocol as above, NEW documented seed (v1.0 used 20260610 and
20260611). Prediction committed before the run in RESULTS.md section 9.4."""


@dataclass(frozen=True)
class MCMCResult:
    """One sampled 1-D posterior with its pre-registered settings and diagnostics."""

    model: str
    param: str
    prior: tuple[float, float]
    n_walkers: int
    n_steps: int
    seed: int
    tau: float
    burn: int
    thin: int
    converged: bool
    acceptance_mean: float
    samples: FloatArray

    def __post_init__(self) -> None:
        self.samples.flags.writeable = False

    @property
    def mean(self) -> float:
        return float(np.mean(self.samples))

    @property
    def std(self) -> float:
        return float(np.std(self.samples, ddof=1))

    def quantile(self, q: float) -> float:
        return float(np.quantile(self.samples, q))


def lcdm_log_prob(chi2: MarginalizedChi2, h0: float = H0_FIDUCIAL) -> Callable[[FloatArray], float]:
    """Flat-prior log-posterior for omega_m on the pre-registered open interval."""
    lo, hi = LCDM_PRIOR

    def log_prob(theta: FloatArray) -> float:
        omega_m = float(theta[0])
        if not lo < omega_m < hi:
            return -np.inf
        return -0.5 * chi2(lcdm_mu_fast(chi2.z, omega_m, h0))

    return log_prob


def janus_prior(chi2: MarginalizedChi2) -> tuple[float, float]:
    """Pre-registered open Janus prior: the full validity domain (q0_min(z_max), 0)."""
    return (janus_q0_min(float(chi2.z.max())), 0.0)


def janus_log_prob(
    chi2: MarginalizedChi2, h0: float = H0_FIDUCIAL
) -> Callable[[FloatArray], float]:
    """Flat-prior log-posterior for q0 on the pre-registered open interval."""
    lo, hi = janus_prior(chi2)

    def log_prob(theta: FloatArray) -> float:
        q0 = float(theta[0])
        if not lo < q0 < hi:
            return -np.inf
        return -0.5 * chi2(janus_mu(chi2.z, q0, h0))

    return log_prob


def run_chain(
    log_prob: Callable[[FloatArray], float],
    prior: tuple[float, float],
    spec: ChainSpec,
    *,
    n_walkers: int = N_WALKERS,
    n_steps: int = N_STEPS,
) -> MCMCResult:
    """Sample one 1-D posterior with fixed seeds and autocorrelation diagnostics.

    Walkers start uniformly over the open prior (inset by INIT_MARGIN); both the
    initialization and the sampler's internal random state derive from ``seed``, so
    two calls with identical arguments produce bit-identical chains (tested).
    """
    lo, hi = prior
    rng = np.random.default_rng(spec.seed)
    inset = INIT_MARGIN * (hi - lo)
    p0 = rng.uniform(lo + inset, hi - inset, size=(n_walkers, 1))

    sampler = EnsembleSampler(n_walkers, 1, log_prob)
    state = np.random.RandomState(spec.seed).get_state(legacy=True)
    if not isinstance(state, tuple):
        msg = "expected the legacy MT19937 state tuple from RandomState.get_state"
        raise TypeError(msg)
    sampler.random_state = state
    sampler.run_mcmc(p0, n_steps)

    tau = float(sampler.get_autocorr_time(quiet=True)[0])
    burn = ceil(3.0 * tau)
    thin = max(1, floor(tau / 2.0))
    samples = sampler.get_chain(discard=burn, thin=thin, flat=True)[:, 0].copy()
    return MCMCResult(
        model=spec.model,
        param=spec.param,
        prior=prior,
        n_walkers=n_walkers,
        n_steps=n_steps,
        seed=spec.seed,
        tau=tau,
        burn=burn,
        thin=thin,
        converged=n_steps > CONVERGENCE_FACTOR * tau,
        acceptance_mean=float(np.mean(sampler.acceptance_fraction)),
        samples=samples,
    )


def sample_lcdm(chi2: MarginalizedChi2, n_steps: int = N_STEPS) -> MCMCResult:
    return run_chain(lcdm_log_prob(chi2), LCDM_PRIOR, LCDM_SPEC, n_steps=n_steps)


def sample_janus(chi2: MarginalizedChi2, n_steps: int = N_STEPS) -> MCMCResult:
    return run_chain(janus_log_prob(chi2), janus_prior(chi2), JANUS_SPEC, n_steps=n_steps)
