"""Download the Pantheon+ release files into data/ and verify their SHA256.

This is the single network step of the project; everything downstream runs offline.
Idempotent: files already present with a matching checksum are left untouched.
Run with ``uv run python scripts/download_data.py``.
"""

import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from janus_refit.data import sha256_of

BASE_URL = (
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/"
    "Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
)
EXPECTED_SHA256 = {
    "Pantheon+SH0ES.dat": "1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8",
    "Pantheon+SH0ES_STAT+SYS.cov": (
        "abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc"
    ),
}
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TIMEOUT_SECONDS = 60


def fetch(name: str, expected: str) -> None:
    target = DATA_DIR / name
    if target.exists():
        if sha256_of(target) == expected:
            print(f"{name}: already present, checksum verified")
            return
        print(f"{name}: present but checksum mismatch, re-downloading")

    url = BASE_URL + urllib.parse.quote(name)
    print(f"{name}: downloading from {url}")
    tmp = target.with_suffix(target.suffix + ".tmp")
    try:
        with (
            urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response,
            tmp.open("wb") as out,
        ):
            shutil.copyfileobj(response, out)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise

    actual = sha256_of(tmp)
    if actual != expected:
        tmp.unlink()
        msg = f"{name}: checksum mismatch after download (got {actual}, expected {expected})"
        raise RuntimeError(msg)
    tmp.replace(target)
    print(f"{name}: downloaded, checksum verified")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, expected in EXPECTED_SHA256.items():
        fetch(name, expected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
