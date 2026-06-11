"""Express MCMC cross-check of the arm-B Janus fit on JLA (v1.1 pre-tag GO).

Protocol identical to RESULTS.md section 6.5 (emcee, fixed NEW seed 20260612,
flat prior on the open validity domain, convergence n_steps > 50 tau, burn-in
3 tau, thinning tau/2). The truncated-Gaussian prediction was committed in
section 9.4 BEFORE this run. STOP rule (GO): if the MCMC std deviates from the
curvature sigma by more than 20%, exit 1 and stop before the tag.
Run with ``uv run python scripts/run_jla_mcmc.py``.
"""

import sys
from pathlib import Path

import numpy as np

from janus_refit.jla import load_jla_sample
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.mcmc import JANUS_JLA_SPEC, janus_log_prob, janus_prior, run_chain

JLA_DIR = Path(__file__).resolve().parents[1] / "data" / "jla"

CURVATURE_Q0 = -0.066887
CURVATURE_SIGMA = 0.028259
"""Frozen arm-B curvature fit (RESULTS.md section 9.4)."""

STOP_REL_DEVIATION = 0.20
"""Pre-tag GO: MCMC-vs-curvature std deviation beyond this triggers STOP."""


def main() -> int:
    sample = load_jla_sample(JLA_DIR)
    chi2 = MarginalizedChi2.from_arrays(z=sample.z_cmb, m_obs=sample.mu_hat, cov=sample.cov)
    result = run_chain(janus_log_prob(chi2), janus_prior(chi2), JANUS_JLA_SPEC)

    chain_path = JLA_DIR / "janus_jla_chain.npz"
    np.savez(chain_path, samples=result.samples, tau=result.tau, seed=result.seed)
    print(f"chain persisted to {chain_path} before any gate evaluation")

    print(
        f"Janus on JLA: seed {result.seed}, {result.n_walkers} walkers x "
        f"{result.n_steps} steps, prior ({result.prior[0]:.6f}, {result.prior[1]:.1f})"
    )
    print(
        f"  tau = {result.tau:.2f}  n/tau = {result.n_steps / result.tau:.1f} "
        f"(converged: {result.converged})  burn = {result.burn}  thin = {result.thin}"
        f"  acceptance = {result.acceptance_mean:.3f}  n_samples = {result.samples.size}"
    )
    q16, q50, q84 = (result.quantile(q) for q in (0.16, 0.50, 0.84))
    p_above = float(np.mean(result.samples > -0.02))
    print(f"  mean = {result.mean:+.6f}  std = {result.std:.6f}")
    print(f"  q16/q50/q84 = {q16:+.6f} / {q50:+.6f} / {q84:+.6f}")
    asymmetry = (q84 - q50) / (q50 - q16)
    print(f"  q84-q50 = {q84 - q50:.6f}  q50-q16 = {q50 - q16:.6f}  ratio = {asymmetry:.4f}")
    print(f"  P(q0 > -0.02) = {p_above:.4f}")

    ratio = result.std / CURVATURE_SIGMA
    print(f"  std vs curvature sigma {CURVATURE_SIGMA}: ratio = {ratio:.4f}")
    if not result.converged:
        print("  CONVERGENCE FAILED (n_steps <= 50 tau): STOP.")
        return 1
    if abs(ratio - 1.0) > STOP_REL_DEVIATION:
        print(f"  STOP: |ratio - 1| = {abs(ratio - 1.0):.4f} > {STOP_REL_DEVIATION}.")
        return 1
    print("  within the 20% gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
