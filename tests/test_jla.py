import numpy as np
import pytest
from helpers import JLA_DIR, requires_jla_data

from janus_refit._types import FloatArray
from janus_refit.fitting import fit_lcdm
from janus_refit.jla import (
    BETOULE_OMEGA_M,
    BETOULE_OMEGA_M_SIGMA,
    BETOULE_STAT_SYS,
    N_SNE,
    OMEGA_M_GATE_N_SIGMA,
    JLANuisances,
    JLASample,
    build_covariance,
    build_mu_hat,
    load_c_eta,
    load_jla_sample,
    read_lcparams,
    read_sigma_mu,
)
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu

pytestmark = requires_jla_data

SUBSAMPLE_50 = np.arange(0, N_SNE, 15)[:50]
"""Fixed 50-SN subsample (every 15th row) for the determinism check."""


@pytest.fixture(scope="module")
def sample() -> JLASample:
    return load_jla_sample(JLA_DIR)


@pytest.fixture(scope="module")
def c_eta() -> FloatArray:
    return load_c_eta(JLA_DIR)


@pytest.fixture(scope="module")
def sigma_mu() -> FloatArray:
    return read_sigma_mu(JLA_DIR / "sigma_mu.txt")


def test_sample_shape_symmetry_and_positive_definiteness(sample: JLASample) -> None:
    assert sample.z_cmb.shape == (N_SNE,)
    assert sample.cov.shape == (N_SNE, N_SNE)
    assert np.isfinite(sample.cov).all()
    assert np.array_equal(sample.cov, sample.cov.T)
    np.linalg.cholesky(sample.cov)


def test_covariance_matches_explicit_a_matrix_construction(
    c_eta: FloatArray, sigma_mu: FloatArray
) -> None:
    """Independent code path: the dense A = A0 + alpha*A1 - beta*A2 of Betoule
    eq. (12) (footnote: (A_k)_ij = delta_{3i, j+k}) against the stride-3 blocks."""
    alpha, beta = BETOULE_STAT_SYS.alpha, BETOULE_STAT_SYS.beta
    rows = np.arange(N_SNE)
    a_matrix = np.zeros((N_SNE, 3 * N_SNE), dtype=np.float64)
    a_matrix[rows, 3 * rows] = 1.0
    a_matrix[rows, 3 * rows + 1] = alpha
    a_matrix[rows, 3 * rows + 2] = -beta
    reference = a_matrix @ c_eta @ a_matrix.T
    sigma_pecvel = (5.0 * 150.0 / 3.0e5) / (np.log(10.0) * sigma_mu[:, 2])
    reference[np.diag_indices_from(reference)] += (
        sigma_mu[:, 0] ** 2 + sigma_mu[:, 1] ** 2 + sigma_pecvel**2
    )
    reference = (reference + reference.T) / 2.0
    built = build_covariance(c_eta, sigma_mu, BETOULE_STAT_SYS)
    assert float(np.max(np.abs(built - reference))) < 1e-14


def test_covariance_and_mu_hat_are_sensitive_to_nuisances(
    c_eta: FloatArray, sigma_mu: FloatArray
) -> None:
    shifted = JLANuisances(alpha=0.2, beta=2.5, m_b1=-19.05, delta_m=-0.070)
    cov_published = build_covariance(c_eta, sigma_mu, BETOULE_STAT_SYS)
    cov_shifted = build_covariance(c_eta, sigma_mu, shifted)
    assert float(np.max(np.abs(cov_published - cov_shifted))) > 1e-6
    table = read_lcparams(JLA_DIR / "jla_lcparams.txt")
    mu_published = build_mu_hat(table, BETOULE_STAT_SYS)
    mu_shifted = build_mu_hat(table, shifted)
    assert float(np.max(np.abs(mu_published - mu_shifted))) > 1e-3


def test_lcparams_first_row_is_pinned() -> None:
    """Row 1 of the v6 release, quoted verbatim in RESULTS.md section 9.1."""
    table = read_lcparams(JLA_DIR / "jla_lcparams.txt")
    first = table.iloc[0]
    assert str(first["name"]) == "03D1au"
    assert float(first["zcmb"]) == 0.503084
    assert float(first["zhel"]) == 0.504300
    assert float(first["mb"]) == 23.001698
    assert float(first["x1"]) == 1.273191
    assert float(first["color"]) == -0.012353
    assert float(first["3rdvar"]) == 9.517
    assert float(table["zcmb"].min()) > 0.01
    assert float(table["zcmb"].max()) < 1.3


def test_host_mass_step_applies_to_the_high_mass_hosts_only() -> None:
    table = read_lcparams(JLA_DIR / "jla_lcparams.txt")
    no_step = JLANuisances(
        alpha=BETOULE_STAT_SYS.alpha,
        beta=BETOULE_STAT_SYS.beta,
        m_b1=BETOULE_STAT_SYS.m_b1,
        delta_m=0.0,
    )
    difference = build_mu_hat(table, BETOULE_STAT_SYS) - build_mu_hat(table, no_step)
    stepped = difference != 0.0
    assert int(stepped.sum()) == 422
    assert np.allclose(difference[stepped], -BETOULE_STAT_SYS.delta_m)
    assert bool((table["3rdvar"].to_numpy(dtype=np.float64)[stepped] > 10.0).all())


def test_sigma_mu_rows_align_with_lcparams_rows(sigma_mu: FloatArray) -> None:
    table = read_lcparams(JLA_DIR / "jla_lcparams.txt")
    z_cmb = table["zcmb"].to_numpy(dtype=np.float64)
    assert float(np.max(np.abs(sigma_mu[:, 2] - z_cmb))) < 1e-6


def test_lcdm_anchor_omega_m_within_published_2sigma(sample: JLASample) -> None:
    """Pre-registered M12 anchor gate (RESULTS.md section 9.2): an arm-B flat-LCDM
    fit on JLA must land within 2 sigma of the published SNe-only Omega_m = 0.295
    +/- 0.034; outside it the conclusion is a pipeline bug, never cosmology."""
    chi2 = MarginalizedChi2.from_arrays(z=sample.z_cmb, m_obs=sample.mu_hat, cov=sample.cov)
    fit = fit_lcdm(chi2)
    half_width = OMEGA_M_GATE_N_SIGMA * BETOULE_OMEGA_M_SIGMA
    assert abs(fit.params["omega_m"] - BETOULE_OMEGA_M) <= half_width


def test_chi2_on_fixed_subsample_is_deterministic_across_loads(sample: JLASample) -> None:
    rebuilt = load_jla_sample(JLA_DIR)
    values: list[float] = []
    for loaded in (sample, rebuilt):
        cov = loaded.cov[np.ix_(SUBSAMPLE_50, SUBSAMPLE_50)].copy()
        chi2 = MarginalizedChi2.from_arrays(
            z=loaded.z_cmb[SUBSAMPLE_50].copy(),
            m_obs=loaded.mu_hat[SUBSAMPLE_50].copy(),
            cov=cov,
        )
        values.append(chi2(janus_mu(chi2.z, -0.1, 70.0)))
    assert values[0] == values[1]
