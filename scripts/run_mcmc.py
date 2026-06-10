"""Run the M8 production MCMC in the pre-registered configuration (RESULTS.md §6.5):
fixed seeds, flat priors on the open intervals, convergence gate n_steps > 50 tau.
Writes corner plots to figures/ and the flattened chains to data/ (gitignored), and
reports the cross-validation of posterior sigmas against the frozen M7 curvature
sigmas. Run with ``uv run python scripts/run_mcmc.py``.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
from corner import corner

from janus_refit.data import load_sample
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.mcmc import MCMCResult, sample_janus, sample_lcdm

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"

M7_FROZEN = {
    "FlatLCDM": (0.331631, 0.018207),
    "Janus": (-0.021010, 0.014767),
}
"""(best fit, curvature sigma) measured at M7 — frozen, RESULTS.md section 7."""

MILNE_CHI2_M7 = 1436.665
SIGMA_INVESTIGATION_THRESHOLD = 0.20

LABELS = {"omega_m": r"$\Omega_m$", "q0": r"$q_0$"}


def describe(result: MCMCResult) -> str:
    q16, q50, q84 = (result.quantile(q) for q in (0.16, 0.5, 0.84))
    best, sigma_ref = M7_FROZEN[result.model]
    rel = result.std / sigma_ref - 1.0
    return (
        f"{result.model:<9} {result.param} = {q50:+.6f} (+{q84 - q50:.6f} / -{q50 - q16:.6f})"
        f"  [16/50/84% quantiles]\n"
        f"  mean = {result.mean:+.6f}  std = {result.std:.6f}"
        f"  | M7 frozen: {best:+.6f} +/- {sigma_ref:.6f}"
        f"  -> sigma rel. diff = {rel:+.2%}\n"
        f"  tau = {result.tau:.2f}  n_steps = {result.n_steps}"
        f" (needs > {50.0 * result.tau:.0f})  burn = {result.burn}  thin = {result.thin}"
        f"  acceptance = {result.acceptance_mean:.3f}  converged = {result.converged}"
    )


def save_corner(result: MCMCResult, path: Path) -> None:
    fig = corner(
        result.samples[:, None],
        labels=[LABELS[result.param]],
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        bins=40,
    )
    fig.savefig(path, dpi=150)


def main() -> int:
    sample = load_sample(
        DATA_DIR / "Pantheon+SH0ES.dat",
        DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
        cache_dir=DATA_DIR,
    )
    chi2 = MarginalizedChi2.from_sample(sample)
    print(f"sample: {sample.z.size} SNe; priors and seeds per RESULTS.md section 6.5")

    FIGURES_DIR.mkdir(exist_ok=True)
    results: list[MCMCResult] = []
    sigma_flags: list[str] = []
    for run, figure_name in ((sample_lcdm, "corner_lcdm.png"), (sample_janus, "corner_janus.png")):
        result = run(chi2)
        results.append(result)
        print(describe(result))
        save_corner(result, FIGURES_DIR / figure_name)
        _, sigma_ref = M7_FROZEN[result.model]
        if abs(result.std / sigma_ref - 1.0) > SIGMA_INVESTIGATION_THRESHOLD:
            sigma_flags.append(result.model)

    lcdm, janus = results
    print(
        f"Janus posterior vs the q0 = 0 domain boundary: max sample = {janus.samples.max():+.6f},"
        f"  P(q0 > -0.005) = {float(np.mean(janus.samples > -0.005)):.4f},"
        f"  P(q0 > {M7_FROZEN['Janus'][0]:+.6f}) = "
        f"{float(np.mean(janus.samples > M7_FROZEN['Janus'][0])):.4f}"
    )
    print(
        f"Milne     (no shape parameter): posterior is the single point"
        f" chi2 = {MILNE_CHI2_M7} (M7, offset profiled analytically) — nothing to sample"
    )

    if not all(result.converged for result in results):
        print("STOP: a chain failed the pre-registered convergence criterion n_steps > 50 tau.")
        return 2
    if sigma_flags:
        print(
            f"INVESTIGATE before publishing contours: sigma rel. diff > "
            f"{SIGMA_INVESTIGATION_THRESHOLD:.0%} vs M7 curvature for: {', '.join(sigma_flags)}"
        )
        return 3

    np.savez(
        DATA_DIR / "mcmc_chains.npz",
        lcdm_omega_m=lcdm.samples,
        janus_q0=janus.samples,
        lcdm_seed=np.int64(lcdm.seed),
        janus_seed=np.int64(janus.seed),
        lcdm_tau=lcdm.tau,
        janus_tau=janus.tau,
    )
    print(f"chains written to {DATA_DIR / 'mcmc_chains.npz'}; figures in {FIGURES_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
