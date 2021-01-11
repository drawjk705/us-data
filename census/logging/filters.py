import inspect
import logging


class CallerFilter(logging.Filter):
    """
    This filter injects class information into the
    log: which class & function called the logger
    """

    def filter(self, record: logging.LogRecord) -> bool:

        frame = inspect.stack()[6].frame
        code = frame.f_code

        if "self" not in frame.f_locals:
            return True

        for m in inspect.getmembers(frame.f_locals["self"], predicate=inspect.ismethod):
            if m[0] == code.co_name:
                try:
                    record.funcName = m[1].__qualname__  # type: ignore
                    return True
                except:
                    pass

        return True
