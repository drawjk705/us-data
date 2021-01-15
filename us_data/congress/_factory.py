# pyright: reportUnknownMemberType=false

import os
from typing import cast

import dotenv
import punq

from us_data.congress._api.fetch import CongressApiFetchService
from us_data.congress._api.interface import ICongressApiFetchService
from us_data.congress._client.congress import Congress
from us_data.congress._config import CongressConfig
from us_data.congress._exceptions import NoCongressApiKeyException
from us_data.congress._members.interface import ICongressMemberRepository
from us_data.congress._members.service import CongressMemberRepository
from us_data.congress._transformation.interface import (
    ICongressDataTransformationService,
)
from us_data.congress._transformation.service import CongressDataTransformationService
from us_data._utils.log.configureLogger import DEFAULT_LOGFILE, configureLogger
from us_data._utils.log.factory import ILoggerFactory, LoggerFactory

transformer = CongressDataTransformationService()
loggerFactory = LoggerFactory()


def getCongress(congressNum: int, logFile: str = DEFAULT_LOGFILE) -> Congress:
    """
    Returns a Congress client object for the given congress

    Args:
        congressNum (int): what number congress (e.g., 116)
        logFile (str)

    Returns:
        Congress: client object
    """

    dotenvPath = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenvPath)  # type: ignore

    apiKey = os.getenv("PROPUBLICA_CONG_KEY")

    if apiKey is None:
        raise NoCongressApiKeyException("Could not find `PROPUBLICA_CONG_KEY in .env")

    config = CongressConfig(congressNum, apiKey)

    container = punq.Container()

    container.register(ICongressDataTransformationService, instance=transformer)
    container.register(CongressConfig, instance=config)
    container.register(ILoggerFactory, instance=loggerFactory)

    container.register(ICongressApiFetchService, CongressApiFetchService)
    container.register(ICongressMemberRepository, CongressMemberRepository)

    container.register(Congress)

    configureLogger(logFile)

    return cast(Congress, container.resolve(Congress))
