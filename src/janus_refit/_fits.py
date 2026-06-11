"""Typed access to the single astropy.io.fits call used by the JLA loader.

astropy ships no type information, so this module confines the untyped surface
(same pattern as tests/oracles.py); everything exported is fully typed.
"""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false, reportUnknownArgumentType=false

from pathlib import Path

import numpy as np
from astropy.io import fits

from janus_refit._types import FloatArray


def read_fits_image(path: Path) -> FloatArray:
    """Read the primary HDU image as a native-byte-order float64 array.

    The released JLA matrices are big-endian on disk; scipy's LAPACK wrappers
    require native order, hence the explicit dtype conversion.
    """
    data = fits.getdata(path)
    return np.asarray(data, dtype=np.float64)
