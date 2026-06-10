from pathlib import Path

import numpy as np
import pytest

from janus_refit.data import (
    PANTHEON_SN_COUNT,
    FloatArray,
    SNSample,
    build_sample,
    load_sample,
    read_covariance,
    read_table,
    validate_covariance,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

requires_data = pytest.mark.skipif(
    not (DATA_DIR / "Pantheon+SH0ES.dat").exists()
    or not (DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov").exists(),
    reason="Pantheon+ files not downloaded (run scripts/download_data.py)",
)

DAT_HEADER = (
    "CID IDSURVEY zHD zHDERR zCMB zCMBERR zHEL zHELERR m_b_corr m_b_corr_err_DIAG "
    "MU_SH0ES MU_SH0ES_ERR_DIAG CEPH_DIST IS_CALIBRATOR USED_IN_SH0ES_HF c cERR"
)


def write_synthetic_release(
    tmp_path: Path,
    z_values: list[float],
    calibrator_flags: list[int],
) -> tuple[Path, Path]:
    rows = [DAT_HEADER]
    for i, (z, flag) in enumerate(zip(z_values, calibrator_flags, strict=True)):
        m = 24.0 + 5.0 * np.log10(z)
        rows.append(
            f"SN{i} 1 {z} 0.001 {z} 0.001 {z} 0.001 {m:.4f} 0.1 "
            f"{m + 19:.4f} 0.1 -9.0 {flag} 0 0.0 0.01"
        )
    dat_path = tmp_path / "synthetic.dat"
    dat_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    n = len(z_values)
    rng = np.random.default_rng(0)
    factor = rng.normal(size=(n, n)) * 0.01
    cov = factor @ factor.T + np.eye(n) * 0.05
    write_covariance_file(tmp_path / "synthetic.cov", n, cov.ravel())
    return dat_path, tmp_path / "synthetic.cov"


def write_covariance_file(cov_path: Path, n: int, values: FloatArray) -> None:
    lines = [str(n)] + [f"{value:.8f}" for value in values]
    cov_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_cut_removes_low_z_and_calibrators(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.005, 0.02, 0.03, 0.05, 0.5],
        calibrator_flags=[0, 0, 1, 0, 0],
    )
    sample = build_sample(dat_path, cov_path, z_min=0.01)
    np.testing.assert_allclose(sample.z, [0.02, 0.05, 0.5])
    assert sample.cov.shape == (3, 3)


def test_covariance_restriction_keeps_cross_terms(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.005, 0.02, 0.05],
        calibrator_flags=[0, 0, 0],
    )
    full = read_covariance(cov_path)
    sample = build_sample(dat_path, cov_path, z_min=0.01)
    np.testing.assert_array_equal(sample.cov, full[1:, 1:])


def test_cache_roundtrip_and_invalidation(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.02, 0.05, 0.5],
        calibrator_flags=[0, 0, 0],
    )
    cache_dir = tmp_path / "cache"
    first = load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir)
    assert (cache_dir / "pantheon_sample_zmin0.01.npz").exists()

    cached = load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir)
    np.testing.assert_array_equal(cached.z, first.z)
    np.testing.assert_array_equal(cached.cov, first.cov)

    with dat_path.open("a", encoding="utf-8") as fh:
        fh.write("SNX 1 0.7 0.001 0.7 0.001 0.7 0.001 25.2 0.1 44.2 0.1 -9.0 0 0 0.0 0.01\n")
    write_covariance_file(cov_path, 4, (np.eye(4) * 0.05).ravel())
    rebuilt = load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir)
    assert rebuilt.z.size == 4


def test_corrupt_cache_is_rebuilt(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.02, 0.05, 0.5],
        calibrator_flags=[0, 0, 0],
    )
    cache_dir = tmp_path / "cache"
    first = load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir)
    cache_path = cache_dir / "pantheon_sample_zmin0.01.npz"
    cache_path.write_bytes(cache_path.read_bytes()[:100])

    recovered = load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir)
    np.testing.assert_array_equal(recovered.z, first.z)
    assert load_sample(dat_path, cov_path, z_min=0.01, cache_dir=cache_dir).z.size == 3


def test_rejects_non_finite_covariance() -> None:
    bad = np.array([[np.nan, 0.0], [0.0, 1.0]])
    with pytest.raises(ValueError, match="non-finite"):
        validate_covariance(bad)


def test_rejects_non_positive_definite() -> None:
    bad = np.array([[1.0, 2.0], [2.0, 1.0]])
    with pytest.raises(ValueError, match="positive definite"):
        validate_covariance(bad)


def test_rejects_asymmetric() -> None:
    bad = np.array([[1.0, 0.5], [0.1, 1.0]])
    with pytest.raises(ValueError, match="symmetric"):
        validate_covariance(bad)


def test_validate_returns_symmetrized() -> None:
    nearly = np.array([[1.0, 0.5 + 1e-9], [0.5, 1.0]])
    result = validate_covariance(nearly)
    np.testing.assert_array_equal(result, result.T)


def test_rejects_declared_size_mismatch(tmp_path: Path) -> None:
    cov_path = tmp_path / "bad.cov"
    write_covariance_file(cov_path, 3, np.ones(4))
    with pytest.raises(ValueError, match="declares N=3"):
        read_covariance(cov_path)


def test_rejects_missing_columns(tmp_path: Path) -> None:
    dat_path = tmp_path / "bad.dat"
    dat_path.write_text("CID zHD m_b_corr\nSN0 0.1 24.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="IS_CALIBRATOR"):
        read_table(dat_path)


def test_rejects_non_finite_magnitudes(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.02, 0.05],
        calibrator_flags=[0, 0],
    )
    lines = dat_path.read_text(encoding="utf-8").splitlines()
    fields = lines[1].split()
    fields[8] = "nan"
    lines[1] = " ".join(fields)
    dat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite"):
        build_sample(dat_path, cov_path, z_min=0.01)


def test_rejects_empty_sample(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.002, 0.005],
        calibrator_flags=[0, 0],
    )
    with pytest.raises(ValueError, match="no SNe survive"):
        build_sample(dat_path, cov_path, z_min=0.01)


def test_rejects_table_covariance_size_mismatch(tmp_path: Path) -> None:
    dat_path, cov_path = write_synthetic_release(
        tmp_path,
        z_values=[0.02, 0.05],
        calibrator_flags=[0, 0],
    )
    write_covariance_file(cov_path, 3, (np.eye(3) * 0.05).ravel())
    with pytest.raises(ValueError, match="rows but covariance"):
        build_sample(dat_path, cov_path, z_min=0.01)


def test_sample_is_immutable_and_consistent() -> None:
    z = np.array([0.1, 0.2])
    m = np.array([24.0, 25.0])
    cov = np.eye(2) * 0.05
    sample = SNSample(z=z, m_b_corr=m, cov=cov, z_min=0.01)
    with pytest.raises(ValueError, match="read-only"):
        sample.z[0] = 1.0

    with pytest.raises(ValueError, match="inconsistent sample shapes"):
        SNSample(z=z, m_b_corr=m, cov=np.eye(3), z_min=0.01)


@requires_data
class TestRealRelease:
    @pytest.fixture(scope="class")
    def sample(self) -> SNSample:
        return load_sample(
            DATA_DIR / "Pantheon+SH0ES.dat",
            DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov",
            cache_dir=DATA_DIR,
        )

    def test_full_release_shape(self) -> None:
        table = read_table(DATA_DIR / "Pantheon+SH0ES.dat")
        assert len(table) == PANTHEON_SN_COUNT
        cov = read_covariance(DATA_DIR / "Pantheon+SH0ES_STAT+SYS.cov")
        assert cov.shape == (PANTHEON_SN_COUNT, PANTHEON_SN_COUNT)
        validate_covariance(cov)

    def test_cosmology_sample_size(self, sample: SNSample) -> None:
        assert 1550 <= sample.z.size <= 1620

    def test_sample_contents(self, sample: SNSample) -> None:
        assert float(sample.z.min()) > 0.01
        assert float(sample.z.max()) < 2.5
        assert bool(np.isfinite(sample.m_b_corr).all())
        validate_covariance(sample.cov)
