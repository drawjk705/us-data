# pyright: reportUnknownMemberType=false

import os
from typing import cast

import dotenv
import punq

from us_data.congress.api.fetch import CongressApiFetchService
from us_data.congress.api.interface import ICongressApiFetchService
from us_data.congress.client.congress import Congress
from us_data.congress.config import CongressConfig
from us_data.congress.exceptions import NoCongressApiKeyException
from us_data.congress.members.interface import ICongressMemberRepository
from us_data.congress.members.service import CongressMemberRepository
from us_data.congress.transformation.interface import ICongressDataTransformationService
from us_data.congress.transformation.service import CongressDataTransformationService
from us_data.utils.log.configureLogger import DEFAULT_LOGFILE, configureLogger
from us_data.utils.log.factory import ILoggerFactory, LoggerFactory

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
