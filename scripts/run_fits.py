"""Run the M7 chi-square fits in the mandated order: LCDM first with its sanity gate,
then Janus and Milne only if the gate passes. Prints raw numbers, no interpretation.
Run with ``uv run python scripts/run_fits.py``.
"""

import sys
from pathlib import Path

from janus_refit.data import load_sample
from janus_refit.fitting import (
    LCDM_CHI2_REFERENCE,
    LCDM_CHI2_TOLERANCE,
    FitResult,
    fit_janus,
    fit_lcdm,
    fit_milne,
)
from janus_refit.likelihood import MarginalizedChi2

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def describe(fit: FitResult) -> str:
    params = ", ".join(
        f"{name} = {value:+.6f} +/- {fit.sigmas[name]:.6f}" for name, value in fit.params.items()
    )
    return (
        f"{fit.model:<9} {params or '(offset only)':<38} "
        f"chi2 = {fit.chi2:9.3f}  dof = {fit.dof}  chi2/dof = {fit.chi2_dof:.4f}"
    )


def main() -> int:
    sample = load_sample(
        DATA_DIR / "Pantheon+SH0ES.dat",
        DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
        cache_dir=DATA_DIR,
    )
    print(f"sample: {sample.z.size} SNe, z in [{sample.z.min():.5f}, {sample.z.max():.5f}]")
    chi2 = MarginalizedChi2.from_sample(sample)

    lcdm = fit_lcdm(chi2)
    print(describe(lcdm))
    if abs(lcdm.chi2 - LCDM_CHI2_REFERENCE) > LCDM_CHI2_TOLERANCE:
        print(
            f"STOP: LCDM best-fit chi2 = {lcdm.chi2:.3f} deviates from the published "
            f"reference {LCDM_CHI2_REFERENCE} (arXiv:2212.07917) by more than "
            f"{LCDM_CHI2_TOLERANCE}. Pipeline bug suspected; Janus and Milne fits NOT run."
        )
        return 2

    print(describe(fit_janus(chi2)))
    print(describe(fit_milne(chi2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
