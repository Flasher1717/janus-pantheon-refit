# Stub-only structural view of the matplotlib surface this repo uses (same approach
# as the corner stub): matplotlib's inline types carry untyped **kwargs that pyright
# strict rejects. Return values this repo ignores are declared as object.
def use(backend: str) -> None: ...
