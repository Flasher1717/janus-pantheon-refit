from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from . import autocorr as autocorr

_LegacyRandomState = tuple[str, NDArray[np.uint32], int, int, float]

class State:
    coords: NDArray[np.float64]
    def __init__(self, coords: NDArray[np.float64], copy: bool = False) -> None: ...

class EnsembleSampler:
    def __init__(
        self,
        nwalkers: int,
        ndim: int,
        log_prob_fn: Callable[[NDArray[np.float64]], float],
    ) -> None: ...
    @property
    def random_state(self) -> _LegacyRandomState: ...
    @random_state.setter
    def random_state(self, state: _LegacyRandomState) -> None: ...
    @property
    def acceptance_fraction(self) -> NDArray[np.float64]: ...
    def run_mcmc(
        self,
        initial_state: NDArray[np.float64] | State | None,
        nsteps: int,
        progress: bool = False,
    ) -> State: ...
    def get_chain(
        self, *, discard: int = 0, thin: int = 1, flat: bool = False
    ) -> NDArray[np.float64]: ...
    def get_autocorr_time(
        self, *, discard: int = 0, thin: int = 1, tol: int = 50, quiet: bool = False
    ) -> NDArray[np.float64]: ...
