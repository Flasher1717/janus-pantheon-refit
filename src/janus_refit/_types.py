"""Shared type aliases (leaf module: keeps the math modules free of IO imports)."""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
