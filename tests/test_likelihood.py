import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from janus_refit._types import FloatArray
from janus_refit.data import SNSample
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import milne_mu


def make_synthetic(n: int = 40, seed: int = 1) -> tuple[MarginalizedChi2, FloatArray]:
    rng = np.random.default_rng(seed)
    z = np.sort(rng.uniform(0.02, 1.5, n))
    m = 24.0 + 5.0 * np.log10(z) + rng.normal(0.0, 0.1, n)
    factor = rng.normal(size=(n, n)) * 0.02
    cov = factor @ factor.T + np.eye(n) * 0.04
    sample = SNSample(z=z, m_b_corr=m, cov=cov, z_min=0.01)
    return MarginalizedChi2.from_sample(sample), cov


def test_matches_explicit_inverse_formula() -> None:
    chi2, cov = make_synthetic()
    mu = 24.2 + 5.0 * np.log10(chi2.z)
    delta = chi2.m_obs - mu
    ones = np.ones_like(delta)
    cinv = np.linalg.inv(cov)
    expected = float(delta @ cinv @ delta - (delta @ cinv @ ones) ** 2 / (ones @ cinv @ ones))
    assert abs(chi2(mu) - expected) < 1e-10 * abs(expected)


def test_equals_numerically_profiled_offset() -> None:
    chi2, cov = make_synthetic(seed=2)
    mu = 24.0 + 5.0 * np.log10(chi2.z)
    delta = chi2.m_obs - mu
    cinv = np.linalg.inv(cov)

    def chi2_at_offset(offset: float) -> float:
        shifted = delta - offset
        return float(shifted @ cinv @ shifted)

    profiled = minimize_scalar(chi2_at_offset, bounds=(-5.0, 5.0), method="bounded")
    assert abs(chi2(mu) - float(profiled.fun)) < 1e-6


def test_invariant_under_additive_offset() -> None:
    chi2, _ = make_synthetic(seed=3)
    mu = 24.0 + 5.0 * np.log10(chi2.z)
    assert abs(chi2(mu + 3.7) - chi2(mu)) < 1e-9 * chi2(mu)


def test_invariant_under_h0_choice() -> None:
    chi2, _ = make_synthetic(seed=4)
    low = chi2(milne_mu(chi2.z, 60.0))
    high = chi2(milne_mu(chi2.z, 80.0))
    assert abs(low - high) < 1e-9 * low


def test_rejects_shape_mismatch() -> None:
    chi2, _ = make_synthetic()
    with pytest.raises(ValueError, match="shape"):
        chi2(np.ones(3))


def test_positive_for_imperfect_model() -> None:
    chi2, _ = make_synthetic(seed=5)
    mu = 24.0 + 5.0 * np.log10(chi2.z)
    assert chi2(mu) > 0.0
