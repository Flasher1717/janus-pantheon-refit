import numpy as np
import pytest
from helpers import DATA_DIR, requires_data

from janus_refit._types import FloatArray
from janus_refit.data import SNSample, load_sample
from janus_refit.fitting import (
    LCDM_CHI2_REFERENCE,
    LCDM_CHI2_TOLERANCE,
    FitResult,
    fit_janus,
    fit_lcdm,
    fit_milne,
)
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu, lcdm_mu, milne_mu


def chi2_from_truth(z: FloatArray, mu_truth: FloatArray) -> MarginalizedChi2:
    n = z.size
    sample = SNSample(z=z, m_b_corr=mu_truth.copy(), cov=np.eye(n) * 0.01, z_min=0.01)
    return MarginalizedChi2.from_sample(sample)


Z_50: FloatArray = np.geomspace(0.02, 1.2, 50)
Z_50.flags.writeable = False


def test_recovers_janus_q0_exactly_on_noiseless_truth() -> None:
    truth = janus_mu(Z_50, -0.1, 70.0) + 0.3
    fit = fit_janus(chi2_from_truth(Z_50, truth))
    assert abs(fit.params["q0"] - (-0.1)) < 1e-5
    assert fit.chi2 < 1e-10
    assert fit.sigmas["q0"] > 0.0
    assert fit.n_params == 2
    assert fit.dof == 48


def test_recovers_lcdm_omega_m_from_quad_oracle_truth() -> None:
    truth = lcdm_mu(Z_50, 0.3, 70.0) - 19.3
    fit = fit_lcdm(chi2_from_truth(Z_50, truth))
    assert abs(fit.params["omega_m"] - 0.3) < 1e-4
    assert fit.chi2 < 1e-8


def test_milne_fit_on_milne_truth() -> None:
    """chi2_marg cancels A - B^2/E exactly in real arithmetic; in float64 the
    residual scales as A * eps (A = offset^2 * E ~ 7e3 here), hence the 1e-9 bound."""
    truth = milne_mu(Z_50, 70.0) + 1.2
    fit = fit_milne(chi2_from_truth(Z_50, truth))
    assert fit.chi2 < 1e-9
    assert fit.params == {}
    assert fit.n_params == 1
    assert fit.dof == 49


def test_fits_are_deterministic() -> None:
    truth = janus_mu(Z_50, -0.08, 70.0)
    chi2 = chi2_from_truth(Z_50, truth)
    first = fit_janus(chi2)
    second = fit_janus(chi2)
    assert first.params["q0"] == second.params["q0"]
    assert first.chi2 == second.chi2


@requires_data
class TestRealPantheonFits:
    @classmethod
    def chi2(cls) -> MarginalizedChi2:
        sample = load_sample(
            DATA_DIR / "Pantheon+SH0ES.dat",
            DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
            cache_dir=DATA_DIR,
        )
        return MarginalizedChi2.from_sample(sample)

    def test_lcdm_chi2_matches_published_value(self) -> None:
        """Sanity gate anchored to the exact published replication for this
        configuration (see LCDM_CHI2_REFERENCE): tighter than the SPEC's a-priori
        [1400, 1500] band it supersedes. Outside the gate the conclusion is a
        pipeline bug, not cosmology."""
        fit = fit_lcdm(self.chi2())
        assert abs(fit.chi2 - LCDM_CHI2_REFERENCE) <= LCDM_CHI2_TOLERANCE

    @pytest.mark.xfail(
        reason="order-of-magnitude check vs the published 2018 JLA fit (q0 = -0.087): "
        "different dataset, standardization and error model (RESULTS.md section 7.3)",
        strict=False,
    )
    def test_janus_q0_order_of_magnitude_vs_published_2018(self) -> None:
        """SPEC requirement: reproduction of the order of magnitude of the published
        2018 q0, xfail-marked because the dataset differs."""
        fit = fit_janus(self.chi2())
        assert -0.87 < fit.params["q0"] < -0.0087

    def test_janus_and_milne_fits_produce_finite_results(self) -> None:
        chi2 = self.chi2()
        janus = fit_janus(chi2)
        milne = fit_milne(chi2)
        for fit in (janus, milne):
            assert np.isfinite(fit.chi2)
            assert fit.chi2 > 0.0
        assert -0.25 < janus.params["q0"] < 0.0


def test_fit_result_chi2_dof() -> None:
    result = FitResult(model="x", params={}, sigmas={}, chi2=100.0, n_points=51, n_params=1)
    assert result.dof == 50
    assert result.chi2_dof == 2.0
