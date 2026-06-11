"""Arm B (M14): the v1.0 pipeline on JLA — three models, one shared likelihood.

Full C(alpha, beta) at the Betoule Table 10 "JLA (stat+sys)" nuisances, analytic
offset profiling, z = zcmb, 740 SNe; AIC/BIC as in RESULTS.md section 6.7. Also
probes the parabolicity of the Janus minimum and its distance to the q0 = 0
domain boundary (the pre-registered no-MCMC escape hatch of section 9.2).
Run with ``uv run python scripts/run_jla_arm_b.py``.
"""

import sys
from pathlib import Path

from janus_refit.comparison import aic, bic
from janus_refit.fitting import FitResult, fit_janus, fit_lcdm, fit_milne
from janus_refit.jla import load_jla_sample
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu

JLA_DIR = Path(__file__).resolve().parents[1] / "data" / "jla"


def describe(fit: FitResult, base_aic: float, base_bic: float) -> None:
    params = ", ".join(
        f"{name} = {value:+.6f} +/- {fit.sigmas[name]:.6f}" for name, value in fit.params.items()
    )
    fit_aic = aic(fit.chi2, fit.n_params)
    fit_bic = bic(fit.chi2, fit.n_params, fit.n_points)
    print(
        f"  {fit.model:<9} chi2 = {fit.chi2:8.3f} / {fit.dof}"
        f"  chi2/dof = {fit.chi2_dof:.4f}"
        f"  AIC = {fit_aic:8.3f} (d {fit_aic - base_aic:+8.3f})"
        f"  BIC = {fit_bic:8.3f} (d {fit_bic - base_bic:+8.3f})"
        f"  {params}"
    )


def main() -> int:
    sample = load_jla_sample(JLA_DIR)
    chi2 = MarginalizedChi2.from_arrays(z=sample.z_cmb, m_obs=sample.mu_hat, cov=sample.cov)
    lcdm = fit_lcdm(chi2)
    janus = fit_janus(chi2)
    milne = fit_milne(chi2)

    print("Arm B on JLA (full C(alpha,beta), stat+sys nuisances, offset profiled, zcmb)")
    base_aic = aic(lcdm.chi2, lcdm.n_params)
    base_bic = bic(lcdm.chi2, lcdm.n_params, lcdm.n_points)
    for fit in (lcdm, janus, milne):
        describe(fit, base_aic, base_bic)

    q0 = janus.params["q0"]
    sigma = janus.sigmas["q0"]
    print("\nJanus minimum diagnostics (no-MCMC escape hatch, RESULTS.md 9.2):")
    print(f"  distance to the q0 = 0 domain boundary: |q0|/sigma = {abs(q0) / sigma:.2f}")
    for k in (1.0, 2.0):
        up = chi2(janus_mu(chi2.z, q0 + k * sigma, 70.0)) - janus.chi2
        down = chi2(janus_mu(chi2.z, q0 - k * sigma, 70.0)) - janus.chi2
        print(
            f"  chi2(q0 +/- {k:.0f} sigma) - chi2_min = {up:.3f} / {down:.3f}"
            f"  (exact parabola: {k * k:.0f})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
