import logging
import sys

from the_census._utils.log.filters import ModuleFilter

DEFAULT_LOG_FILE = "census.log"


def configureLogger(log_file: str, datasetName: str) -> None:
    """
    sets up logger for the project

    Args:
        log_file (str): the name of the file that log output will be sent to
    """

    logFormat = "[{0} %(levelname)s] %(asctime)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s".format(
        datasetName
    )
    dateFormat = "%Y-%m-%d %H:%M:%S%z"

    logger = logging.getLogger("census")
    logger.setLevel(logging.NOTSET)

    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setLevel(logging.INFO)
    formatter = logging.Formatter(logFormat, datefmt=dateFormat)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    rootHandler = logging.FileHandler(log_file)
    rootHandler.setLevel(logging.NOTSET)
    rootHandler.addFilter(ModuleFilter())
    rootHandler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, format=logFormat, handlers=[rootHandler])
