from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

requires_data = pytest.mark.skipif(
    not (DATA_DIR / "Pantheon+SH0ES.dat").exists()
    or not (DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov").exists(),
    reason="Pantheon+ files not downloaded (run scripts/download_data.py)",
)
