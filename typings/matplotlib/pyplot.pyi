from os import PathLike

import numpy as np
from numpy.typing import NDArray

class Axes:
    def errorbar(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
        *,
        yerr: NDArray[np.float64] | None = None,
        fmt: str = "",
        ms: float = ...,
        elinewidth: float = ...,
        color: str = ...,
        alpha: float = ...,
        label: str = ...,
    ) -> object: ...
    def plot(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
        style: str = "-",
        *,
        lw: float = ...,
        color: str = ...,
        label: str = ...,
    ) -> object: ...
    def axhline(
        self, y: float = 0.0, *, color: str = ..., lw: float = ..., label: str = ...
    ) -> object: ...
    def set_xscale(self, scale: str) -> None: ...
    def set_xlabel(self, label: str) -> None: ...
    def set_ylabel(self, label: str) -> None: ...
    def set_ylim(self, bottom: float, top: float) -> None: ...
    def legend(self, *, loc: str = ..., fontsize: str | float = ...) -> object: ...

class Figure:
    def savefig(self, fname: str | PathLike[str], *, dpi: float = ...) -> None: ...
    def tight_layout(self) -> None: ...

def subplots(*, figsize: tuple[float, float] = ...) -> tuple[Figure, Axes]: ...
