"""JLA sample (Betoule et al. 2014): distance estimator and full covariance.

Everything here is implemented from the release files pinned by
scripts/download_data.py and from Betoule et al. 2014 (A&A 568, A22), with the
release's own reference implementations as cross-checks (RESULTS.md section 9.1):

- Distance estimator, eqs. (4)-(5): mu_hat = m_B* - (M_B^1 + Delta_M * step) +
  alpha * X1 - beta * C, where step applies to hosts with log10 stellar mass
  strictly above ``scriptmcut = 10.0`` (jla.dataset; strict ">" per jla.cc).
  SNe without a measured host mass already carry a low-mass-bin value in the
  released 3rdvar column (eq. 5 "otherwise" branch never sees a sentinel).

- Covariance, eqs. (11)-(13): C(alpha, beta) = A C_eta A^T
  + diag(5 sigma_z / (z ln 10))^2 + diag(sigma_lens^2) + diag(sigma_coh^2),
  with C_eta the sum of the eight released FITS components. The eta vector is
  interleaved per SN, (m_B*_1, X1_1, C_1, ..., m_B*_740, X1_740, C_740), so the
  740x740 blocks are stride-3 slices of the 2220x2220 matrices. The peculiar
  velocity term uses c*sigma_z = 150 km/s with c = 3e5 km/s, kept verbatim from
  the release's covmat example.py so the construction is bit-comparable.

Redshift convention: the release's reference test (src/test.cc, documented to
reproduce -2 ln L = 682.9) evaluates the model at zcmb alone, although the ReadMe
prose says both zcmb and zhel are needed; the primary convention here follows the
executable reference (zcmb), and the heliocentric factor is only ever applied as a
labeled sensitivity (RESULTS.md section 9.1).
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from janus_refit._fits import read_fits_image
from janus_refit._types import FloatArray
from janus_refit.data import validate_covariance

N_SNE = 740
"""Full JLA sample size; the 2018 paper and Betoule et al. 2014 both use all 740."""

HOST_MASS_CUT_LOG10 = 10.0
"""jla.dataset ``scriptmcut = 10.0``; applied with strict ">" as in jla.cc."""

PECULIAR_VELOCITY_KM_S = 150.0
"""Betoule et al. 2014, eq. (13) context: "We follow C11 in using c sigma_z = 150 km/s"."""

C_LIGHT_EXAMPLE_KM_S = 3.0e5
"""Speed of light as approximated in the release's covmat example.py (``3e5``), kept
verbatim so our covariance matches the reference construction exactly."""

C_ETA_COMPONENTS = (
    "C_stat.fits",
    "C_cal.fits",
    "C_model.fits",
    "C_bias.fits",
    "C_host.fits",
    "C_dust.fits",
    "C_pecvel.fits",
    "C_nonia.fits",
)
"""The eight terms of eq. (11), as distributed in covmat_v6.tgz."""

BETOULE_OMEGA_M = 0.295
BETOULE_OMEGA_M_SIGMA = 0.034
"""Betoule et al. 2014, abstract and Table 10 row "JLA (stat+sys)": the SNe-only
flat-LCDM constraint Omega_m = 0.295 +/- 0.034."""

OMEGA_M_GATE_N_SIGMA = 2.0
"""Pre-registered anchor gate (RESULTS.md section 9.2): the arm-B flat-LCDM fit on
JLA must land within 2 sigma of the published SNe-only Omega_m; outside means
pipeline bug until proven otherwise."""


@dataclass(frozen=True)
class JLANuisances:
    """The four fixed standardization parameters of the distance estimator."""

    alpha: float
    beta: float
    m_b1: float
    delta_m: float


BETOULE_STAT_SYS = JLANuisances(alpha=0.141, beta=3.101, m_b1=-19.05, delta_m=-0.070)
"""Betoule et al. 2014, Table 10, row "JLA (stat+sys)" — independently confirmed by
the nuisance vector {0.141, 3.101, -19.05, -0.070} hardcoded in the release's
reference test src/test.cc."""


@dataclass(frozen=True)
class JLASample:
    """The 740-SN Hubble diagram with fixed-nuisance mu_hat and its covariance."""

    z_cmb: FloatArray
    z_hel: FloatArray
    mu_hat: FloatArray
    cov: FloatArray

    def __post_init__(self) -> None:
        n = self.z_cmb.size
        shapes_ok = (
            self.z_hel.shape == self.z_cmb.shape
            and self.mu_hat.shape == self.z_cmb.shape
            and self.cov.shape == (n, n)
        )
        if not shapes_ok:
            msg = (
                f"inconsistent sample shapes: z_cmb {self.z_cmb.shape}, "
                f"z_hel {self.z_hel.shape}, mu_hat {self.mu_hat.shape}, cov {self.cov.shape}"
            )
            raise ValueError(msg)
        for array in (self.z_cmb, self.z_hel, self.mu_hat, self.cov):
            array.flags.writeable = False


def read_lcparams(path: Path) -> pd.DataFrame:
    """Parse jla_lcparams.txt; the header line starts with '#name'."""
    table = pd.read_csv(path, sep=r"\s+")
    table.columns = [str(column).lstrip("#") for column in table.columns]
    required = {"zcmb", "zhel", "mb", "dmb", "x1", "dx1", "color", "dcolor", "3rdvar"}
    missing = required - set(table.columns)
    if missing:
        msg = f"{path} lacks expected columns: {sorted(missing)}"
        raise ValueError(msg)
    if len(table) != N_SNE:
        msg = f"{path} has {len(table)} rows, expected {N_SNE}"
        raise ValueError(msg)
    return table


def read_sigma_mu(path: Path) -> FloatArray:
    """Read sigma_mu.txt: columns (sigma_coh, sigma_lens, z), one row per SN.

    The third column is the redshift, not an uncertainty: the peculiar-velocity
    diagonal term is computed from it (release ReadMe and example.py).
    """
    values = np.loadtxt(path, dtype=np.float64)
    if values.ndim != 2 or values.shape != (N_SNE, 3):
        msg = f"{path} has shape {values.shape}, expected ({N_SNE}, 3)"
        raise ValueError(msg)
    return values


def load_c_eta(jla_dir: Path) -> FloatArray:
    """Sum the eight released components of eq. (11) into C_eta (2220x2220)."""
    c_eta = read_fits_image(jla_dir / C_ETA_COMPONENTS[0])
    for name in C_ETA_COMPONENTS[1:]:
        c_eta += read_fits_image(jla_dir / name)
    expected = (3 * N_SNE, 3 * N_SNE)
    if c_eta.shape != expected:
        msg = f"C_eta has shape {c_eta.shape}, expected {expected}"
        raise ValueError(msg)
    return c_eta


def build_mu_hat(table: pd.DataFrame, nuisances: JLANuisances) -> FloatArray:
    """Distance estimator of Betoule et al. 2014, eqs. (4)-(5), at fixed nuisances."""
    mb = table["mb"].to_numpy(dtype=np.float64)
    x1 = table["x1"].to_numpy(dtype=np.float64)
    color = table["color"].to_numpy(dtype=np.float64)
    host_mass = table["3rdvar"].to_numpy(dtype=np.float64)
    step = (host_mass > HOST_MASS_CUT_LOG10).astype(np.float64)
    m_b = nuisances.m_b1 + nuisances.delta_m * step
    return mb - m_b + nuisances.alpha * x1 - nuisances.beta * color


def build_covariance(
    c_eta: FloatArray, sigma_mu: FloatArray, nuisances: JLANuisances
) -> FloatArray:
    """Covariance of mu_hat, eq. (13), via stride-3 blocks of the interleaved eta."""
    n = sigma_mu.shape[0]
    if c_eta.shape != (3 * n, 3 * n):
        msg = f"C_eta shape {c_eta.shape} inconsistent with {n} SNe"
        raise ValueError(msg)
    coefficients = (1.0, nuisances.alpha, -nuisances.beta)
    cov = np.zeros((n, n), dtype=np.float64)
    for i, coefficient_i in enumerate(coefficients):
        for j, coefficient_j in enumerate(coefficients):
            cov += (coefficient_i * coefficient_j) * c_eta[i::3, j::3]
    sigma_coh = sigma_mu[:, 0]
    sigma_lens = sigma_mu[:, 1]
    z = sigma_mu[:, 2]
    sigma_pecvel = (5.0 * PECULIAR_VELOCITY_KM_S / C_LIGHT_EXAMPLE_KM_S) / (np.log(10.0) * z)
    cov[np.diag_indices_from(cov)] += sigma_coh**2 + sigma_lens**2 + sigma_pecvel**2
    return validate_covariance(cov)


def load_jla_sample(jla_dir: Path, nuisances: JLANuisances = BETOULE_STAT_SYS) -> JLASample:
    """Load and assemble the full JLA sample from the pinned release files."""
    table = read_lcparams(jla_dir / "jla_lcparams.txt")
    sigma_mu = read_sigma_mu(jla_dir / "sigma_mu.txt")
    z_cmb = table["zcmb"].to_numpy(dtype=np.float64)
    mu_hat = build_mu_hat(table, nuisances)
    if not (np.isfinite(z_cmb).all() and np.isfinite(mu_hat).all()):
        msg = f"{jla_dir} light-curve parameters contain non-finite values"
        raise ValueError(msg)
    misalignment = float(np.max(np.abs(sigma_mu[:, 2] - z_cmb)))
    if misalignment > 1e-6:
        msg = (
            f"sigma_mu.txt row order does not match jla_lcparams.txt (max |dz| = {misalignment:g})"
        )
        raise ValueError(msg)
    return JLASample(
        z_cmb=z_cmb,
        z_hel=table["zhel"].to_numpy(dtype=np.float64),
        mu_hat=mu_hat,
        cov=build_covariance(load_c_eta(jla_dir), sigma_mu, nuisances),
    )
