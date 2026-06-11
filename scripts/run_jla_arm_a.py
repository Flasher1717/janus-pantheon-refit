"""Arm A (M13): the closed variant grid of RESULTS.md section 9.2 on JLA.

Eight runs (4 error models x 2 host-step treatments), nuisances fixed at the
Betoule Table 10 "JLA (stat+sys)" values, free parameters q0 + offset (profiled),
z = zcmb, all 740 SNe. Criteria C1/C2/C3 and the principal-variant selection rule
are the pre-registered ones; a non-reproduction is reported as-is, never an error.
Run with ``uv run python scripts/run_jla_arm_a.py``.
"""

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

from janus_refit.fitting import FitResult, fit_janus
from janus_refit.jla import (
    ARM_A_C1_STRONG_HALF_WIDTH,
    ARM_A_C2_SIGMA_BOUNDS,
    ARM_A_C3_CHI2_HALF_WIDTH,
    ARM_A_CHI2_TARGET,
    ARM_A_ERROR_MODELS,
    ARM_A_Q0_TARGET,
    ARM_A_SIGMA_TARGET,
    BETOULE_STAT,
    BETOULE_STAT_SYS,
    JLANuisances,
    arm_a_covariance,
    build_mu_hat,
    heliocentric_factor,
    load_c_eta,
    read_lcparams,
    read_sigma_mu,
)
from janus_refit.likelihood import MarginalizedChi2

JLA_DIR = Path(__file__).resolve().parents[1] / "data" / "jla"


def criteria(fit: FitResult) -> tuple[bool, bool, bool, bool]:
    q0 = fit.params["q0"]
    sigma = fit.sigmas["q0"]
    c1 = abs(q0 - ARM_A_Q0_TARGET) <= ARM_A_SIGMA_TARGET
    strong = abs(q0 - ARM_A_Q0_TARGET) <= ARM_A_C1_STRONG_HALF_WIDTH
    c2 = ARM_A_C2_SIGMA_BOUNDS[0] <= sigma <= ARM_A_C2_SIGMA_BOUNDS[1]
    c3 = abs(fit.chi2 - ARM_A_CHI2_TARGET) <= ARM_A_C3_CHI2_HALF_WIDTH
    return c1, strong, c2, c3


def all_pass(flags: tuple[bool, bool, bool, bool]) -> bool:
    c1, _, c2, c3 = flags
    return c1 and c2 and c3


def report(label: str, fit: FitResult) -> None:
    c1, strong, c2, c3 = criteria(fit)
    flags = (
        f"C1={'PASS' if c1 else 'fail'}{'(strong)' if strong else ''} "
        f"C2={'PASS' if c2 else 'fail'} C3={'PASS' if c3 else 'fail'}"
    )
    print(
        f"  {label:<28} q0 = {fit.params['q0']:+.6f} +/- {fit.sigmas['q0']:.6f}"
        f"  chi2 = {fit.chi2:8.3f} / {fit.dof}  {flags}"
    )


def step_nuisances(base: JLANuisances, host_step: bool) -> JLANuisances:
    return base if host_step else replace(base, delta_m=0.0)


def main() -> int:
    table = read_lcparams(JLA_DIR / "jla_lcparams.txt")
    sigma_mu = read_sigma_mu(JLA_DIR / "sigma_mu.txt")
    c_eta = load_c_eta(JLA_DIR)
    z_cmb = table["zcmb"].to_numpy(dtype=np.float64)
    z_hel = table["zhel"].to_numpy(dtype=np.float64)

    print(
        "Arm A grid (RESULTS.md 9.2, closed): targets "
        f"q0* = {ARM_A_Q0_TARGET}, sigma* = {ARM_A_SIGMA_TARGET}, "
        f"chi2* = {ARM_A_CHI2_TARGET} (dof 738)"
    )
    fits: dict[tuple[str, bool], FitResult] = {}
    for error_model in ARM_A_ERROR_MODELS:
        cov = arm_a_covariance(error_model, table, c_eta, sigma_mu, BETOULE_STAT_SYS)
        for host_step in (True, False):
            nuisances = step_nuisances(BETOULE_STAT_SYS, host_step)
            mu_hat = build_mu_hat(table, nuisances)
            fit = fit_janus(MarginalizedChi2.from_arrays(z=z_cmb, m_obs=mu_hat, cov=cov))
            fits[(error_model, host_step)] = fit
            report(f"{error_model} / {'step' if host_step else 'no-step'}", fit)

    passers = {key: fit for key, fit in fits.items() if all_pass(criteria(fit))}
    if passers:
        principal_key = min(passers, key=lambda key: abs(passers[key].chi2 - ARM_A_CHI2_TARGET))
        verdict = "method reproduced and error model identified"
    else:
        principal_key = min(fits, key=lambda key: abs(fits[key].params["q0"] - ARM_A_Q0_TARGET))
        verdict = "non-reproduction, least-distant variant"
    principal = fits[principal_key]
    error_model, host_step = principal_key
    print(f"\npassers (C1 AND C2 AND C3): {len(passers)}/8")
    print(f"principal variant ({verdict}): {error_model} / {'step' if host_step else 'no-step'}")

    print("\nsensitivities on the principal variant (labeled, delta q0):")
    nuisances = step_nuisances(BETOULE_STAT_SYS, host_step)
    mu_hat = build_mu_hat(table, nuisances)
    cov = arm_a_covariance(error_model, table, c_eta, sigma_mu, BETOULE_STAT_SYS)

    mu_hat_helio = mu_hat - heliocentric_factor(z_cmb, z_hel)
    fit_helio = fit_janus(MarginalizedChi2.from_arrays(z=z_cmb, m_obs=mu_hat_helio, cov=cov))
    print(
        f"  zhel factor applied:        q0 = {fit_helio.params['q0']:+.6f}"
        f"  (delta q0 = {fit_helio.params['q0'] - principal.params['q0']:+.6f},"
        f" chi2 = {fit_helio.chi2:.3f})"
    )

    nuisances_stat = step_nuisances(BETOULE_STAT, host_step)
    mu_hat_stat = build_mu_hat(table, nuisances_stat)
    cov_stat = arm_a_covariance(error_model, table, c_eta, sigma_mu, nuisances_stat)
    fit_stat = fit_janus(MarginalizedChi2.from_arrays(z=z_cmb, m_obs=mu_hat_stat, cov=cov_stat))
    print(
        f"  Table 10 'JLA (stat)' row:  q0 = {fit_stat.params['q0']:+.6f}"
        f"  (delta q0 = {fit_stat.params['q0'] - principal.params['q0']:+.6f},"
        f" chi2 = {fit_stat.chi2:.3f})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
