import logging
import sys
from census.logging.filters import CallerFilter

DEFAULT_LOGFILE = "census.log"


def configureLogger(logFile: str):
    """
    sets up logger for the project

    Args:
        logFile (str): the name of the file that log output will be sent to
    """
    logFormat = "[%(levelname)s] %(asctime)s [%(funcName)s:%(lineno)d] %(message)s"
    dateFormat = "%Y-%m-%d %H:%M:%S %z"

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    logger.addFilter(CallerFilter())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(logFormat, datefmt=dateFormat)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.FileHandler(logFile)
    handler.setLevel(logging.NOTSET)
    formatter = logging.Formatter(logFormat, datefmt=dateFormat)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
