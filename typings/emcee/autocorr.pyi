import numpy as np
from numpy.typing import NDArray

class AutocorrError(Exception):
    tau: NDArray[np.float64]
