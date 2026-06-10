# corner.corner returns a matplotlib.figure.Figure at runtime. It is declared here
# through a private structural type covering exactly the surface this repo uses,
# because matplotlib's own savefig signature carries untyped **kwargs that pyright
# strict rejects. _CornerFigure is a stub-only name, never importable at runtime.
from collections.abc import Sequence
from os import PathLike

import numpy as np
from numpy.typing import NDArray

class _CornerFigure:
    def savefig(self, fname: str | PathLike[str], *, dpi: float = ...) -> None: ...

def corner(
    data: NDArray[np.float64],
    *,
    labels: Sequence[str] | None = None,
    truths: Sequence[float] | None = None,
    quantiles: Sequence[float] | None = None,
    show_titles: bool = False,
    title_fmt: str = ".2f",
    bins: int = 20,
) -> _CornerFigure: ...
