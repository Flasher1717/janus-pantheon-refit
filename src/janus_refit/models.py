"""Distance-modulus models: flat LambdaCDM, Janus (D'Agostini & Petit 2018), Milne.

Every formula implements an equation recorded in RESULTS.md section 2 ("Model
equations as extracted"); each function cites its paper equation number. The Janus
relation is implemented in BOTH published algebraic forms — eq. (26)/(28) and
eq. (29) — so that a transcription error in either fails the cross-consistency test.

Domain validation here raises ValueError to catch programmer error. Likelihood
wrappers (M7/M8) must enforce parameter priors themselves — e.g. return -inf for
q0 outside (janus_q0_min(z_max), 0) — BEFORE calling these functions, so that an
out-of-domain sampler proposal never turns into an exception mid-run.
"""

import numpy as np
from scipy.integrate import quad

from janus_refit._types import FloatArray

C_LIGHT_KM_S = 299792.458


def _mu_from_dl_mpc(dl_mpc: FloatArray) -> FloatArray:
    return 5.0 * np.log10(dl_mpc) + 25.0


def _validate_redshifts(z: FloatArray) -> None:
    if z.ndim != 1 or z.size == 0:
        msg = f"redshift array must be one-dimensional and non-empty (shape {z.shape})"
        raise ValueError(msg)
    if not (np.isfinite(z).all() and (z > 0.0).all()):
        msg = "redshifts must be finite and strictly positive"
        raise ValueError(msg)


def _validate_h0(h0: float) -> None:
    if h0 <= 0.0:
        msg = f"h0 must be positive (got {h0})"
        raise ValueError(msg)


def lcdm_mu(z: FloatArray, omega_m: float, h0: float) -> FloatArray:
    """Distance modulus for flat LambdaCDM (the reference model).

    Standard FLRW result: d_L = (1 + z) * (c/H0) * int_0^z dz'/E(z') with
    E(z) = sqrt(Om (1+z)^3 + 1 - Om). Accuracy is set by the quad tolerance
    (relative 1e-11), validated against astropy.cosmology to < 1e-6 mag. This is
    the slow reference implementation; the fit stage will pin a vectorized
    fixed-order Gauss-Legendre fast path against it at the same gate.
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    if omega_m < 0.0:
        msg = f"omega_m must be non-negative (got {omega_m})"
        raise ValueError(msg)

    def inverse_e(zp: float) -> float:
        return 1.0 / float(np.sqrt(omega_m * (1.0 + zp) ** 3 + 1.0 - omega_m))

    comoving = np.array(
        [quad(inverse_e, 0.0, float(zi), epsabs=0.0, epsrel=1e-11)[0] for zi in z],
        dtype=np.float64,
    )
    dl_mpc = (C_LIGHT_KM_S / h0) * (1.0 + z) * comoving
    return _mu_from_dl_mpc(dl_mpc)


_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(16)


def lcdm_mu_fast(z: FloatArray, omega_m: float, h0: float) -> FloatArray:
    """Production evaluator for flat LambdaCDM: 16-node Gauss-Legendre per [0, z_i].

    12 nodes measured at 2.2e-12 mag vs the quad oracle over omega_m in [0.2, 1.0];
    16 nodes reach the float64 floor (7.1e-15 mag), comfortably under the 1e-12 gate.

    Same formula as lcdm_mu, with the comoving integral evaluated by a fixed-order
    Gauss-Legendre rule mapped onto each [0, z_i] (fully vectorized, no interpolation,
    no sortedness assumption). Pinned against the quad oracle lcdm_mu at < 1e-12 mag
    by a permanent test; the oracle stays in the suite.
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    if omega_m < 0.0:
        msg = f"omega_m must be non-negative (got {omega_m})"
        raise ValueError(msg)
    half = 0.5 * z
    zp = half[:, None] * (_GL_NODES[None, :] + 1.0)
    integrand = 1.0 / np.sqrt(omega_m * (1.0 + zp) ** 3 + 1.0 - omega_m)
    comoving = (half[:, None] * _GL_WEIGHTS[None, :] * integrand).sum(axis=1)
    dl_mpc = (C_LIGHT_KM_S / h0) * (1.0 + z) * comoving
    return _mu_from_dl_mpc(dl_mpc)


def janus_q0_min(z_max: float) -> float:
    """Lower edge of the Janus validity domain for a sample reaching z_max.

    The condition stated with eq. (7) of the 2018 paper, 1 + 2 q0 z > 0, holds for
    the whole sample iff q0 > -1/(2 z_max). The bound itself is excluded.
    """
    if z_max <= 0.0:
        msg = f"z_max must be positive (got {z_max})"
        raise ValueError(msg)
    return -0.5 / z_max


def _validate_janus_domain(z: FloatArray, q0: float) -> None:
    """Validity conditions stated with eq. (7) of the 2018 paper: q0 < 0, 1 + 2 q0 z > 0."""
    if not q0 < 0.0:
        msg = f"Janus model requires q0 < 0 (got {q0})"
        raise ValueError(msg)
    if not (1.0 + 2.0 * q0 * z > 0.0).all():
        msg = f"1 + 2 q0 z must stay positive over the sample (q0={q0}, z_max={float(z.max())})"
        raise ValueError(msg)


def janus_mu_terrell(z: FloatArray, q0: float, h0: float) -> FloatArray:
    """Janus distance modulus, Terrell form — 2018 paper eq. (29), same bracket as eq. (7).

    mu = 5 log10[ z + z^2 (1 - q0) / (1 + q0 z + sqrt(1 + 2 q0 z)) ] + cst, with the
    constant made explicit through d_L = (c/H0) * bracket. Numerically regular at
    q0 -> 0^-, where the bracket reduces to z + z^2/2 (the Milne relation).
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    _validate_janus_domain(z, q0)
    root = np.sqrt(1.0 + 2.0 * q0 * z)
    bracket = z + z * z * (1.0 - q0) / (1.0 + q0 * z + root)
    return _mu_from_dl_mpc((C_LIGHT_KM_S / h0) * bracket)


def janus_mu_mattig(z: FloatArray, q0: float, h0: float) -> FloatArray:
    """Janus distance modulus, Mattig-like form — 2018 paper eq. (26)/(28).

    The printed bracket [q0 z + (1 - q0)(1 - sqrt(1 + 2 q0 z))] / q0^2 suffers
    catastrophic cancellation in float64 (measured 6e-11 relative error at
    q0 = -0.01, z = 0.01). It is evaluated here through the exact conjugate identity
    1 - sqrt(1 + 2 q0 z) = -2 q0 z / (1 + sqrt(1 + 2 q0 z)), derived from the (26)/(28)
    expression alone, which gives bracket = z (sqrt(1 + 2 q0 z) - 1 + 2 q0) /
    (q0 (1 + sqrt(1 + 2 q0 z))). A residual sqrt(1+eps)-1 cancellation of order
    eps_machine/|q0| in magnitude remains as q0 -> 0^- (tests pin it); use the
    Terrell form in that regime. See RESULTS.md section 5.
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    _validate_janus_domain(z, q0)
    root = np.sqrt(1.0 + 2.0 * q0 * z)
    bracket = z * (root - 1.0 + 2.0 * q0) / (q0 * (1.0 + root))
    return _mu_from_dl_mpc((C_LIGHT_KM_S / h0) * bracket)


def janus_mu(z: FloatArray, q0: float, h0: float) -> FloatArray:
    """Production evaluator for Janus: unified cancellation-free bracket.

    Exact algebraic reduction of eq. (29): with s = sqrt(1 + 2 q0 z), the identity
    1 + q0 z + s = (1 + s)^2 / 2 (since 2 q0 z = s^2 - 1) and 1 - q0 =
    (2z + 1 - s^2)/(2z) turn the eq. (29) bracket into 2 z (1 + s + z) / (1 + s)^2 —
    no division by q0, no subtraction, regular at q0 -> 0^- (reduces to z + z^2/2).
    Derivation recorded in RESULTS.md section 5. Pinned against both published forms
    at < 1e-12 mag by permanent tests; the published forms stay in the suite.
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    _validate_janus_domain(z, q0)
    root = np.sqrt(1.0 + 2.0 * q0 * z)
    bracket = 2.0 * z * (1.0 + root + z) / (1.0 + root) ** 2
    return _mu_from_dl_mpc((C_LIGHT_KM_S / h0) * bracket)


def milne_mu(z: FloatArray, h0: float) -> FloatArray:
    """Distance modulus for the empty (Milne) universe: d_L = (c/H0)(z + z^2/2).

    Zero shape parameters. This is exactly the q0 = 0 limit of the Janus eq. (29)
    bracket (the 2018 paper notes eq. (29) "is valid for q0 = 0").
    """
    _validate_redshifts(z)
    _validate_h0(h0)
    bracket = z + 0.5 * z * z
    return _mu_from_dl_mpc((C_LIGHT_KM_S / h0) * bracket)
