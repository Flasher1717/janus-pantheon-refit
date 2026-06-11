from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

requires_data = pytest.mark.skipif(
    not (DATA_DIR / "Pantheon+SH0ES.dat").exists()
    or not (DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov").exists(),
    reason="Pantheon+ files not downloaded (run scripts/download_data.py)",
)

JLA_DIR = DATA_DIR / "jla"

_JLA_FILES = (
    "jla_lcparams.txt",
    "sigma_mu.txt",
    "C_stat.fits",
    "C_cal.fits",
    "C_model.fits",
    "C_bias.fits",
    "C_host.fits",
    "C_dust.fits",
    "C_pecvel.fits",
    "C_nonia.fits",
)

requires_jla_data = pytest.mark.skipif(
    not all((JLA_DIR / name).exists() for name in _JLA_FILES),
    reason="JLA files not downloaded (run scripts/download_data.py)",
)
