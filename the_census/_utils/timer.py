import logging
import time
from typing import Any, Callable, Dict, TypeVar, cast

_Func = TypeVar("_Func", bound=Callable[..., Any])


def timer(func: _Func) -> _Func:
    def wrapper(*args: Any, **kwargs: Dict[Any, Any]) -> Any:
        start_time = time.perf_counter()

        retval = func(*args, **kwargs)

        end_time = time.perf_counter()

        elapsedMs = (end_time - start_time) * 1000

        logging.getLogger(__name__).debug(
            f"[{func.__qualname__}] - duration: {elapsedMs:.2f}ms"
        )

        return retval

    return cast(_Func, wrapper)  # type: ignore
