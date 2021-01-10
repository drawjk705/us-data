import logging


class PathFilter(logging.Filter):
    """
    This filter injects class information into the
    log: which class & function called the logger
    """

    def filter(self, record: logging.LogRecord) -> bool:
        pathName = record.pathname
        splitName = pathName.split("us-stats/")
        if len(splitName) > 1:
            record.pathname = splitName[1]
        else:
            record.pathname = splitName[0]

        return True
