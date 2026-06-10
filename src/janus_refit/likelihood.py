"""Chi-square with the full covariance and analytic marginalization of the offset.

The additive distance-modulus offset (absorbing M_B and 5 log10(c/H0), i.e. the
"cst" the 2018 paper itself fits) is profiled out analytically: with
Delta = m_obs - mu_model(z; theta) and C the full STAT+SYS covariance,

    chi2_marg = A - B^2/E,  A = Delta^T C^-1 Delta,  B = Delta^T C^-1 1,
    E = 1^T C^-1 1.

The model-independent + ln(E / 2 pi) term of full Bayesian marginalization is
identical for every model on shared data and is therefore omitted. All C^-1 products
are evaluated through one cached Cholesky factorization (scipy cho_factor/cho_solve);
the covariance is never explicitly inverted.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import cho_factor, cho_solve

from janus_refit._types import FloatArray
from janus_refit.data import SNSample


@dataclass(frozen=True)
class MarginalizedChi2:
    """Offset-marginalized chi-square for one dataset, shared by all models."""

    z: FloatArray
    m_obs: FloatArray
    _cho: tuple[FloatArray, bool] = field(repr=False)
    _cinv_ones: FloatArray = field(repr=False)
    _e: float

    @classmethod
    def from_sample(cls, sample: SNSample) -> "MarginalizedChi2":
        cho = cho_factor(sample.cov, lower=True)
        ones = np.ones_like(sample.m_b_corr)
        cinv_ones = cho_solve(cho, ones)
        return cls(
            z=sample.z,
            m_obs=sample.m_b_corr,
            _cho=cho,
            _cinv_ones=cinv_ones,
            _e=float(ones @ cinv_ones),
        )

    @property
    def n_points(self) -> int:
        return int(self.z.size)

    def __call__(self, mu_model: FloatArray) -> float:
        if mu_model.shape != self.m_obs.shape:
            msg = f"mu_model shape {mu_model.shape} != data shape {self.m_obs.shape}"
            raise ValueError(msg)
        delta = self.m_obs - mu_model
        a = float(delta @ cho_solve(self._cho, delta))
        b = float(delta @ self._cinv_ones)
        return a - b * b / self._e

    def best_offset(self, mu_model: FloatArray) -> float:
        """The profiled additive offset B/E at which the chi-square minimum over
        the offset is attained (Goliath et al. 2001, eq. 21)."""
        if mu_model.shape != self.m_obs.shape:
            msg = f"mu_model shape {mu_model.shape} != data shape {self.m_obs.shape}"
            raise ValueError(msg)
        delta = self.m_obs - mu_model
        return float(delta @ self._cinv_ones) / self._e
