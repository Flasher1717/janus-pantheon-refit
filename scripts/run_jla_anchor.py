"""Arm-B flat-LCDM anchor fit on JLA (M12): the pre-registered Omega_m gate.

Run with ``uv run python scripts/run_jla_anchor.py``. Exits 1 when the gate fails:
outside |Omega_m - 0.295| <= 2 x 0.034 the conclusion is "pipeline bug until proven
otherwise" (RESULTS.md section 9.2), never cosmology.
"""

import sys
from pathlib import Path

from janus_refit.fitting import fit_lcdm
from janus_refit.jla import (
    BETOULE_OMEGA_M,
    BETOULE_OMEGA_M_SIGMA,
    OMEGA_M_GATE_N_SIGMA,
    load_jla_sample,
)
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import lcdm_mu_fast

JLA_DIR = Path(__file__).resolve().parents[1] / "data" / "jla"


def main() -> int:
    sample = load_jla_sample(JLA_DIR)
    chi2 = MarginalizedChi2.from_arrays(z=sample.z_cmb, m_obs=sample.mu_hat, cov=sample.cov)
    fit = fit_lcdm(chi2)
    omega_m = fit.params["omega_m"]
    offset = chi2.best_offset(lcdm_mu_fast(sample.z_cmb, omega_m, 70.0))
    half_width = OMEGA_M_GATE_N_SIGMA * BETOULE_OMEGA_M_SIGMA
    gate_pass = abs(omega_m - BETOULE_OMEGA_M) <= half_width

    print("flat-LCDM on JLA (740 SNe, full C(alpha,beta), offset profiled, z = zcmb)")
    print(f"  Omega_m         = {omega_m:.6f} +/- {fit.sigmas['omega_m']:.6f} (conditional)")
    print(f"  chi2 / dof      = {fit.chi2:.3f} / {fit.dof}")
    print("  published       = 0.295 +/- 0.034 (marginal); chi2 682.9 / 735 (5-param fit)")
    print(f"  profiled offset = {offset:+.6f} mag (absorbs M_B and 5 log10(c/H0))")
    verdict = "PASS" if gate_pass else "FAIL"
    print(f"  gate |Omega_m - {BETOULE_OMEGA_M}| <= {half_width:.3f}: {verdict}")
    if not gate_pass:
        print("  GATE FAILED: pipeline bug until proven otherwise (RESULTS.md 9.2). STOP.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
