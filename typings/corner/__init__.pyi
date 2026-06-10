from collections.abc import Sequence
from os import PathLike

import numpy as np
from numpy.typing import NDArray

class CornerFigure:
    def savefig(self, fname: str | PathLike[str], *, dpi: float = ...) -> None: ...

def corner(
    data: NDArray[np.float64],
    *,
    labels: Sequence[str] | None = None,
    truths: Sequence[float] | None = None,
    quantiles: Sequence[float] | None = None,
    show_titles: bool = False,
    title_fmt: str = ".4f",
    bins: int = 20,
) -> CornerFigure: ...
