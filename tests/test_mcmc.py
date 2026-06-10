import numpy as np
from helpers import DATA_DIR, requires_data

from janus_refit.data import SNSample, load_sample
from janus_refit.fitting import fit_janus
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.mcmc import (
    LCDM_PRIOR,
    LCDM_SPEC,
    ChainSpec,
    janus_log_prob,
    janus_prior,
    lcdm_log_prob,
    run_chain,
    sample_janus,
    sample_lcdm,
)
from janus_refit.models import janus_mu, janus_q0_min

Q0_TRUTH = -0.1
H0_TRUTH = 70.0

M7_FROZEN_LCDM_OMEGA_M = 0.331631
"""Frozen M7 best fit (RESULTS.md section 7) — the MCMC must not move it."""


def synthetic_chi2(n: int = 50, sigma: float = 0.1, seed: int = 7) -> MarginalizedChi2:
    rng = np.random.default_rng(seed)
    z = np.geomspace(0.02, 1.2, n)
    m = janus_mu(z, Q0_TRUTH, H0_TRUTH) - 19.3 + rng.normal(0.0, sigma, n)
    sample = SNSample(z=z, m_b_corr=m, cov=np.eye(n) * sigma**2, z_min=0.01)
    return MarginalizedChi2.from_sample(sample)


class TestPreRegisteredPriors:
    def test_lcdm_log_prob_is_neg_inf_outside_open_interval(self) -> None:
        log_prob = lcdm_log_prob(synthetic_chi2())
        for omega_m in (0.005, 0.01, 1.0, 1.5):
            assert log_prob(np.array([omega_m])) == -np.inf
        assert np.isfinite(log_prob(np.array([0.3])))

    def test_janus_log_prob_is_neg_inf_outside_open_interval_without_raising(self) -> None:
        chi2 = synthetic_chi2()
        log_prob = janus_log_prob(chi2)
        lo, hi = janus_prior(chi2)
        assert hi == 0.0
        assert lo == janus_q0_min(float(chi2.z.max()))
        for q0 in (lo - 0.1, lo, 0.0, 0.1):
            assert log_prob(np.array([q0])) == -np.inf
        assert np.isfinite(log_prob(np.array([Q0_TRUTH])))


class TestSyntheticChains:
    def test_chains_are_bit_identical_for_fixed_seed(self) -> None:
        chi2 = synthetic_chi2()
        first = sample_janus(chi2, n_steps=800)
        second = sample_janus(chi2, n_steps=800)
        assert np.array_equal(first.samples, second.samples)
        assert first.tau == second.tau
        assert first.burn == second.burn

    def test_different_seed_produces_different_chain(self) -> None:
        """Pins the seed mechanism itself (emcee's random_state setter fails
        silently by design): if seeding silently stopped working, both chains
        would derive from the same fallback state and this test would catch it."""
        chi2 = synthetic_chi2()
        log_prob = janus_log_prob(chi2)
        prior = janus_prior(chi2)
        base = ChainSpec(model="Janus", param="q0", seed=11)
        other = ChainSpec(model="Janus", param="q0", seed=12)
        first = run_chain(log_prob, prior, base, n_steps=400)
        second = run_chain(log_prob, prior, other, n_steps=400)
        assert not np.array_equal(first.samples, second.samples)

    def test_lcdm_synthetic_chain_is_deterministic(self) -> None:
        chi2 = synthetic_chi2()
        first = sample_lcdm(chi2, n_steps=600)
        second = sample_lcdm(chi2, n_steps=600)
        assert np.array_equal(first.samples, second.samples)

    def test_janus_posterior_recovers_truth_and_converges(self) -> None:
        result = sample_janus(synthetic_chi2(), n_steps=1500)
        assert result.converged
        assert result.n_steps > 50.0 * result.tau
        assert abs(result.quantile(0.5) - Q0_TRUTH) < 4.0 * result.std
        assert 0.1 < result.acceptance_mean < 0.9

    def test_mcmc_sigma_matches_curvature_sigma_within_20_percent(self) -> None:
        """The M8 GO cross-validation threshold: posterior std vs M7-style Hessian
        sigma; on a near-Gaussian 1-D synthetic posterior they must agree well
        inside the 20% investigation trigger."""
        chi2 = synthetic_chi2()
        fit = fit_janus(chi2)
        result = sample_janus(chi2, n_steps=2000)
        assert abs(result.std / fit.sigmas["q0"] - 1.0) < 0.2

    def test_samples_are_immutable_and_inside_prior(self) -> None:
        chi2 = synthetic_chi2()
        result = sample_janus(chi2, n_steps=800)
        lo, hi = janus_prior(chi2)
        assert not result.samples.flags.writeable
        assert float(result.samples.min()) > lo
        assert float(result.samples.max()) < hi


@requires_data
class TestRealPantheonMCMC:
    @classmethod
    def full_sample(cls) -> SNSample:
        return load_sample(
            DATA_DIR / "Pantheon+SH0ES.dat",
            DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
            cache_dir=DATA_DIR,
        )

    def test_deterministic_on_50_sn_subsample(self) -> None:
        """SPEC determinism check: full pipeline on a fixed 50-SN subsample of the
        real data, fixed seed, run twice — bit-identical chains."""
        sample = self.full_sample()
        idx = np.linspace(0, sample.z.size - 1, 50).astype(np.int64)
        sub = SNSample(
            z=sample.z[idx],
            m_b_corr=sample.m_b_corr[idx],
            cov=sample.cov[np.ix_(idx, idx)],
            z_min=sample.z_min,
        )
        chi2 = MarginalizedChi2.from_sample(sub)
        first = sample_lcdm(chi2, n_steps=600)
        second = sample_lcdm(chi2, n_steps=600)
        assert np.array_equal(first.samples, second.samples)

    def test_lcdm_posterior_median_consistent_with_frozen_m7_fit(self) -> None:
        chi2 = MarginalizedChi2.from_sample(self.full_sample())
        result = run_chain(
            lcdm_log_prob(chi2),
            LCDM_PRIOR,
            LCDM_SPEC,
            n_walkers=16,
            n_steps=500,
        )
        assert abs(result.quantile(0.5) - M7_FROZEN_LCDM_OMEGA_M) < 3.0 * result.std
