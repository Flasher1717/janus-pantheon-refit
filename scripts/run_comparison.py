"""Print the M9 model-comparison table from the frozen M7 chi-squares and write the
Hubble-diagram residual figure (relative to the frozen flat-LCDM best fit).
Run with ``uv run python scripts/run_comparison.py``.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from janus_refit.comparison import aic, bic
from janus_refit.data import load_sample
from janus_refit.likelihood import MarginalizedChi2
from janus_refit.models import janus_mu, lcdm_mu_fast, milne_mu
from janus_refit.reference import (
    M7_JANUS_CHI2,
    M7_JANUS_Q0,
    M7_LCDM_CHI2,
    M7_LCDM_OMEGA_M,
    M7_MILNE_CHI2,
    N_PARAMS,
    N_SNE,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"
H0_FIDUCIAL = 70.0

FROZEN_CHI2 = {
    "FlatLCDM": M7_LCDM_CHI2,
    "Janus": M7_JANUS_CHI2,
    "Milne": M7_MILNE_CHI2,
}


def print_table() -> None:
    stats = {
        name: (
            chi2_value,
            N_SNE - N_PARAMS[name],
            aic(chi2_value, N_PARAMS[name]),
            bic(chi2_value, N_PARAMS[name], N_SNE),
        )
        for name, chi2_value in FROZEN_CHI2.items()
    }
    aic_ref, bic_ref = stats["FlatLCDM"][2], stats["FlatLCDM"][3]
    header = (
        f"{'model':<9} {'k':>2} {'chi2':>9} {'dof':>5} {'chi2/dof':>9}"
        f" {'AIC':>10} {'BIC':>10} {'dAIC':>8} {'dBIC':>8}"
    )
    print(header)
    for name, (chi2_value, dof, aic_value, bic_value) in stats.items():
        print(
            f"{name:<9} {N_PARAMS[name]:>2} {chi2_value:9.3f} {dof:5d}"
            f" {chi2_value / dof:9.4f} {aic_value:10.3f} {bic_value:10.3f}"
            f" {aic_value - aic_ref:+8.3f} {bic_value - bic_ref:+8.3f}"
        )
    print(
        f"Janus vs Milne: dAIC = {stats['Janus'][2] - stats['Milne'][2]:+.3f}"
        f"  dBIC = {stats['Janus'][3] - stats['Milne'][3]:+.3f}"
    )


def write_residuals_figure() -> Path:
    sample = load_sample(
        DATA_DIR / "Pantheon+SH0ES.dat",
        DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
        cache_dir=DATA_DIR,
    )
    chi2 = MarginalizedChi2.from_sample(sample)
    z = sample.z
    mu = {
        "FlatLCDM": lcdm_mu_fast(z, M7_LCDM_OMEGA_M, H0_FIDUCIAL),
        "Janus": janus_mu(z, M7_JANUS_Q0, H0_FIDUCIAL),
        "Milne": milne_mu(z, H0_FIDUCIAL),
    }
    predicted = {name: model_mu + chi2.best_offset(model_mu) for name, model_mu in mu.items()}
    residuals = sample.m_b_corr - predicted["FlatLCDM"]

    order = np.argsort(z)
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.errorbar(
        z,
        residuals,
        yerr=np.sqrt(np.diag(sample.cov)),
        fmt=".",
        ms=2.0,
        elinewidth=0.4,
        color="0.6",
        alpha=0.5,
        label="data - FlatLCDM (diagonal errors, illustrative only)",
    )
    ax.axhline(0.0, color="k", lw=1.0, label="FlatLCDM best fit (M7, frozen)")
    for name, style in (("Janus", "--"), ("Milne", ":")):
        delta_curve = predicted[name] - predicted["FlatLCDM"]
        ax.plot(z[order], delta_curve[order], style, lw=1.5, label=f"{name} best fit (M7, frozen)")
    ax.set_xscale("log")
    ax.set_xlabel("zHD")
    ax.set_ylabel("residual [mag]")
    ax.set_ylim(-1.0, 1.0)
    ax.legend(loc="upper left", fontsize="small")
    fig.tight_layout()
    path = FIGURES_DIR / "residuals.png"
    fig.savefig(path, dpi=150)
    return path


def main() -> int:
    print_table()
    FIGURES_DIR.mkdir(exist_ok=True)
    path = write_residuals_figure()
    print(f"residual figure written to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
