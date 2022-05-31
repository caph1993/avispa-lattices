import itertools
from typing import Generator, Iterable, List, cast, TypeVar

F = TypeVar('F')


def product_list(*iterables: Iterable[F], repeat=1,
                 out=None) -> Generator[List[F], None, None]:
    'same as itertools.product, but mutates the output instead of making tuples'
    dims = [list(it) for it in iterables] * repeat
    n = len(dims)
    if out is not None:
        assert len(out) == n, f'Incompatible output shape'

    out = [None] * n if out is None else out
    out = cast(List[F], out)

    def backtrack(i):
        if i == n:
            yield out
        else:
            for x in dims[i]:
                out[i] = x
                yield from backtrack(i + 1)

    yield from backtrack(0)


def cartesian(*sizes: int):
    return product_list(*(range(size) for size in sizes))