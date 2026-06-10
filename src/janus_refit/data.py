"""Pantheon+ data loading: table parsing, redshift cut, covariance restriction, caching.

The release README mandates the full STAT+SYS covariance for cosmology fits; the
``*_DIAG`` columns are explicitly not usable. The cosmology-only sample follows the
published analysis choices: ``zHD > z_min`` (peculiar-velocity floor) and exclusion of
the Cepheid-host calibrators (no SH0ES calibration in this project).
"""

import hashlib
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from janus_refit._types import FloatArray

PANTHEON_SN_COUNT = 1701
DEFAULT_Z_MIN = 0.01
REDSHIFT_COLUMN = "zHD"
MAGNITUDE_COLUMN = "m_b_corr"
CALIBRATOR_COLUMN = "IS_CALIBRATOR"

SYMMETRY_TOL = 1e-6
"""Relative tolerance on |C - C^T|: the released file carries ~3e-8 absolute asymmetry
from decimal rounding of its text values, which is physically negligible."""

_CACHE_SCHEMA = 1
"""Bump whenever build_sample semantics or cached fields change."""


@dataclass(frozen=True)
class SNSample:
    """Hubble-diagram sample after cuts, with its restricted STAT+SYS covariance."""

    z: FloatArray
    m_b_corr: FloatArray
    cov: FloatArray
    z_min: float

    def __post_init__(self) -> None:
        n = self.z.size
        if self.m_b_corr.shape != self.z.shape or self.cov.shape != (n, n):
            msg = (
                f"inconsistent sample shapes: z {self.z.shape}, "
                f"m_b_corr {self.m_b_corr.shape}, cov {self.cov.shape}"
            )
            raise ValueError(msg)
        for array in (self.z, self.m_b_corr, self.cov):
            array.flags.writeable = False


def sha256_of(path: Path) -> str:
    with path.open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()


def read_table(dat_path: Path) -> pd.DataFrame:
    table = pd.read_csv(dat_path, sep=r"\s+")
    missing = {REDSHIFT_COLUMN, MAGNITUDE_COLUMN, CALIBRATOR_COLUMN} - set(table.columns)
    if missing:
        msg = f"{dat_path} lacks expected columns: {sorted(missing)}"
        raise ValueError(msg)
    return table


def read_covariance(cov_path: Path) -> FloatArray:
    """Read the release covariance format: first line N, then N*N values sequentially."""
    with cov_path.open(encoding="ascii") as fh:
        n = int(fh.readline())
    values = pd.read_csv(cov_path, skiprows=1, header=None, dtype=np.float64).to_numpy()
    if values.size != n * n:
        msg = f"{cov_path} declares N={n} but contains {values.size} values"
        raise ValueError(msg)
    return values.reshape(n, n)


def validate_covariance(cov: FloatArray) -> FloatArray:
    """Check square / finite / symmetric within rounding / positive definite.

    Returns the symmetrized matrix ``(C + C^T) / 2``, the one downstream code must use.
    """
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        msg = f"covariance is not square: shape {cov.shape}"
        raise ValueError(msg)
    if not np.isfinite(cov).all():
        msg = "covariance contains non-finite values"
        raise ValueError(msg)
    asymmetry = float(np.max(np.abs(cov - cov.T)))
    scale = float(np.max(np.abs(cov)))
    if asymmetry > SYMMETRY_TOL * scale:
        msg = f"covariance is not symmetric: max |C - C^T| = {asymmetry:g}"
        raise ValueError(msg)
    symmetrized = (cov + cov.T) / 2.0
    try:
        np.linalg.cholesky(symmetrized)
    except np.linalg.LinAlgError as exc:
        msg = "covariance is not positive definite (Cholesky failed)"
        raise ValueError(msg) from exc
    return symmetrized


def build_sample(dat_path: Path, cov_path: Path, z_min: float = DEFAULT_Z_MIN) -> SNSample:
    """Parse the release files and restrict to the cosmology sample."""
    table = read_table(dat_path)
    cov = read_covariance(cov_path)
    if len(table) != cov.shape[0]:
        msg = f"table has {len(table)} rows but covariance is {cov.shape[0]}x{cov.shape[0]}"
        raise ValueError(msg)

    z_all = table[REDSHIFT_COLUMN].to_numpy(dtype=np.float64)
    m_all = table[MAGNITUDE_COLUMN].to_numpy(dtype=np.float64)
    is_calibrator = table[CALIBRATOR_COLUMN].to_numpy(dtype=np.int64)
    if not (np.isfinite(z_all).all() and np.isfinite(m_all).all()):
        msg = f"{dat_path} contains non-finite {REDSHIFT_COLUMN}/{MAGNITUDE_COLUMN} values"
        raise ValueError(msg)

    keep = (z_all > z_min) & (is_calibrator == 0)
    if not keep.any():
        msg = f"no SNe survive the cuts (z_min={z_min})"
        raise ValueError(msg)
    cov_cut = validate_covariance(cov[np.ix_(keep, keep)])
    return SNSample(z=z_all[keep], m_b_corr=m_all[keep], cov=cov_cut, z_min=z_min)


def load_sample(
    dat_path: Path,
    cov_path: Path,
    z_min: float = DEFAULT_Z_MIN,
    cache_dir: Path | None = None,
) -> SNSample:
    """Load the cosmology sample, using an ``.npz`` cache keyed on source checksums."""
    if cache_dir is None:
        return build_sample(dat_path, cov_path, z_min)

    sources_key = f"v{_CACHE_SCHEMA}:{sha256_of(dat_path)}:{sha256_of(cov_path)}"
    cache_path = cache_dir / f"pantheon_sample_zmin{z_min}.npz"
    cached = _read_cache(cache_path, sources_key, z_min)
    if cached is not None:
        return cached

    sample = build_sample(dat_path, cov_path, z_min)
    _write_cache(cache_path, sample, sources_key)
    return sample


def _read_cache(cache_path: Path, sources_key: str, z_min: float) -> SNSample | None:
    """Return the cached sample, or None when absent, stale, foreign or corrupt."""
    if not cache_path.exists():
        return None
    try:
        with np.load(cache_path) as cached:
            if str(cached["sources_key"]) != sources_key:
                return None
            return SNSample(
                z=cached["z"], m_b_corr=cached["m_b_corr"], cov=cached["cov"], z_min=z_min
            )
    except (zipfile.BadZipFile, KeyError, OSError, ValueError):
        return None


def _write_cache(cache_path: Path, sample: SNSample, sources_key: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".npz.tmp")
    with tmp.open("wb") as fh:
        np.savez(
            fh,
            z=sample.z,
            m_b_corr=sample.m_b_corr,
            cov=sample.cov,
            sources_key=np.str_(sources_key),
        )
    tmp.replace(cache_path)
