"""Download the Pantheon+ and JLA release files into data/ and verify their SHA256.

This is the single network step of the project; everything downstream runs offline.
Idempotent: files already present with a matching checksum are left untouched.
Run with ``uv run python scripts/download_data.py``.

v1.1 adds the JLA release (Betoule et al. 2014) from its original first-party host
supernovae.in2p3.fr (static since 2015-03-18): two SHA256-pinned tarballs from which
only the members needed for the cosmology fit are extracted into data/jla/, each
member pinned individually. Only the v6 archives are valid (the release notes record
that C_stat.fits was not positive definite before V5).
"""

import shutil
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

from janus_refit.data import sha256_of

PANTHEON_BASE_URL = (
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/"
    "Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
)
PANTHEON_SHA256 = {
    "Pantheon+SH0ES.dat": "1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8",
    "Pantheon+SH0ES_STAT+SYS.cov": (
        "abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc"
    ),
}

JLA_BASE_URL = "https://supernovae.in2p3.fr/sdss_snls_jla/"
JLA_ARCHIVE_SHA256 = {
    "jla_likelihood_v6.tgz": "2f06277628ab53ca6590c7da679714b39b2b5a0973c2f8978cebdb1626e762f4",
    "covmat_v6.tgz": "dbb80d7bb11b1cd343d1550c34f3376897a15e98d11171138edcab274eb1e7dd",
}
JLA_MEMBER_SHA256: dict[str, dict[str, str]] = {
    "jla_likelihood_v6.tgz": {
        "jla_likelihood_v6/data/jla_lcparams.txt": (
            "dd6f88100235d591f51cc651eda8657358809f41d7ea954fcdb84f6ac779c243"
        ),
    },
    "covmat_v6.tgz": {
        "covmat/C_stat.fits": "7e584cd7f0b70e9a9aeeb7b9d96fd4ed838e288f3db693b1f54993c319cfb95c",
        "covmat/C_cal.fits": "dcad7e050dadc28114050ea909cab3462d60b184a24ced4de6369207f53c7ec9",
        "covmat/C_model.fits": "0809f02c09df4930f29e06cac1c373586aee862946398b74811fae38c38f4888",
        "covmat/C_bias.fits": "beacbc8a2f03fe1e58ccc2ef63c9fcf7061debce77c619773321ff2f1653572d",
        "covmat/C_host.fits": "5d7d666620581851ad6bde1d6c3e7272ef85e33a46e59ab24897c7e8c2d2f50c",
        "covmat/C_dust.fits": "61c3b865ef4a91ec0f3da0b4019e560f1da69e5865895c26526f3283912c9516",
        "covmat/C_pecvel.fits": "66a62ae9fb16cbe609ff01f525d2272e72c72422edc3b618d4728f35b735af03",
        "covmat/C_nonia.fits": "f9d60b47772bbbdf1d7f0a0e1dc61fed67b24e2ffb2787a65cb8c1d635391b4f",
        "covmat/sigma_mu.txt": "cd17cdd80ba9d2be82c86807075c7bbc28350dafeae5e85c910657ff965cebf6",
    },
}

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ARCHIVE_DIR = DATA_DIR / "archives"
JLA_DIR = DATA_DIR / "jla"
TIMEOUT_SECONDS = 60


def download(url: str, target: Path, expected: str) -> None:
    if target.exists():
        if sha256_of(target) == expected:
            print(f"{target.name}: already present, checksum verified")
            return
        print(f"{target.name}: present but checksum mismatch, re-downloading")

    print(f"{target.name}: downloading from {url}")
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
        msg = f"{target.name}: checksum mismatch after download (got {actual}, expected {expected})"
        raise RuntimeError(msg)
    tmp.replace(target)
    print(f"{target.name}: downloaded, checksum verified")


def member_target(member: str) -> Path:
    return JLA_DIR / PurePosixPath(member).name


def pending_members(members: dict[str, str]) -> dict[str, str]:
    pending: dict[str, str] = {}
    for member, expected in members.items():
        target = member_target(member)
        if target.exists() and sha256_of(target) == expected:
            print(f"{target.name}: already extracted, checksum verified")
        else:
            pending[member] = expected
    return pending


def extract_members(archive: Path, pending: dict[str, str]) -> None:
    remaining = dict(pending)
    with tarfile.open(archive, "r:gz") as tar:
        for info in tar:
            expected = remaining.pop(info.name, None)
            if expected is None:
                continue
            source = tar.extractfile(info)
            if source is None:
                msg = f"{archive.name}: member {info.name} is not a regular file"
                raise RuntimeError(msg)
            target = member_target(info.name)
            tmp = target.with_suffix(target.suffix + ".tmp")
            try:
                with source, tmp.open("wb") as out:
                    shutil.copyfileobj(source, out)
            except BaseException:
                tmp.unlink(missing_ok=True)
                raise
            actual = sha256_of(tmp)
            if actual != expected:
                tmp.unlink()
                msg = (
                    f"{target.name}: checksum mismatch after extraction "
                    f"(got {actual}, expected {expected})"
                )
                raise RuntimeError(msg)
            tmp.replace(target)
            print(f"{target.name}: extracted, checksum verified")
            if not remaining:
                return
    msg = f"{archive.name}: members not found in archive: {sorted(remaining)}"
    raise RuntimeError(msg)


def fetch_jla(archive_name: str) -> None:
    pending = pending_members(JLA_MEMBER_SHA256[archive_name])
    if not pending:
        return
    archive = ARCHIVE_DIR / archive_name
    download(
        JLA_BASE_URL + urllib.parse.quote(archive_name), archive, JLA_ARCHIVE_SHA256[archive_name]
    )
    extract_members(archive, pending)


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, expected in PANTHEON_SHA256.items():
        download(PANTHEON_BASE_URL + urllib.parse.quote(name), DATA_DIR / name, expected)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    JLA_DIR.mkdir(parents=True, exist_ok=True)
    for archive_name in JLA_ARCHIVE_SHA256:
        fetch_jla(archive_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
