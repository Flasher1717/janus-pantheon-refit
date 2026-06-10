"""Typed access to the astropy.cosmology oracle used by the model tests.

astropy ships no type information, so this single module confines the untyped
surface; everything exported is fully typed and the pyright relaxations below
apply to this file only.
"""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false

import numpy as np
from astropy.cosmology import FlatLambdaCDM, LambdaCDM

from janus_refit._types import FloatArray


def astropy_flat_lcdm_mu(z: FloatArray, omega_m: float, h0: float) -> FloatArray:
    cosmo = FlatLambdaCDM(H0=h0, Om0=omega_m)  # pyright: ignore[reportCallIssue]
    return np.asarray(
        cosmo.distmod(z).value,  # pyright: ignore[reportAttributeAccessIssue]
        dtype=np.float64,
    )


def astropy_empty_universe_mu(z: FloatArray, h0: float) -> FloatArray:
    cosmo = LambdaCDM(H0=h0, Om0=0.0, Ode0=0.0)  # pyright: ignore[reportCallIssue]
    return np.asarray(
        cosmo.distmod(z).value,  # pyright: ignore[reportAttributeAccessIssue]
        dtype=np.float64,
    )
