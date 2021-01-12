from census.log.filters import ModuleFilter
import logging
import sys

DEFAULT_LOGFILE = "census.log"


def configureLogger(logFile: str) -> None:
    """
    sets up logger for the project

    Args:
        logFile (str): the name of the file that log output will be sent to
    """

    logFormat = (
        "[%(levelname)s] %(asctime)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    dateFormat = "%Y-%m-%d %H:%M:%S%z"

    logger = logging.getLogger("census")
    logger.setLevel(logging.NOTSET)

    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.INFO)
    formatter = logging.Formatter(logFormat, datefmt=dateFormat)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    fileHandler = logging.FileHandler(logFile)
    fileHandler.setLevel(logging.NOTSET)
    formatter = logging.Formatter(logFormat, datefmt=dateFormat)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    rootHandler = logging.FileHandler(logFile)
    rootHandler.setLevel(logging.NOTSET)
    rootHandler.addFilter(ModuleFilter())

    logging.basicConfig(level=logging.DEBUG, format=logFormat, handlers=[rootHandler])
