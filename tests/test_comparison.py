from math import log

from janus_refit.comparison import aic, bic


def test_aic_definition() -> None:
    assert aic(100.0, 2) == 104.0


def test_bic_definition() -> None:
    assert bic(100.0, 2, 1580) == 100.0 + 2.0 * log(1580)


def test_bic_penalizes_extra_parameters_more_than_aic_for_large_n() -> None:
    assert bic(0.0, 1, 1580) > aic(0.0, 1)


def test_differences_cancel_shared_chi2() -> None:
    assert aic(50.0, 2) - aic(30.0, 2) == 20.0
    assert abs(bic(50.0, 1, 100) - bic(30.0, 2, 100) - (20.0 - log(100))) < 1e-12
