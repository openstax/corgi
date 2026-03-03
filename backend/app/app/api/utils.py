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

            # The next step in our time-based step function
            point_in_time = step(int(time()), ttl)
            # Glue the point_in_time to our args so that the hash changes if
            # we reach the point in time or any of our arguments change
            new_hash = hash(
                (point_in_time, args, tuple(sorted(kwargs.items())))
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
