from collections.abc import Callable
from time import time
from typing import Awaitable, ParamSpec, TypeVar, cast

T = TypeVar("T")
P = ParamSpec("P")


def step(t: int, period: int) -> int:
    return (t // period + 1) * period


def async_memoize_timed(ttl: int, maxsize=25):
    def wrapper(f: Callable[P, Awaitable[T]]):
        idx = 0
        pairs: list[tuple[int, T]] = [
            cast(tuple[int, T], (None, None))
        ] * maxsize
        results = dict(pairs)

        async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            nonlocal results, idx, pairs

            new_hash = hash(
                (step(int(time()), ttl), args, tuple(sorted(kwargs.items())))
            )
            result = results.get(new_hash, None)
            if result is None:
                result = await f(*args, **kwargs)
                pair = (new_hash, result)
                pairs[idx] = pair
                results = dict(pairs)
                idx = (idx + 1) % maxsize
            return result

        return inner

    return wrapper
