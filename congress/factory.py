# pyright: reportUnknownMemberType=false

import os
from typing import cast

import dotenv
import punq

from congress.api.fetch import CongressApiFetchService
from congress.api.interface import ICongressApiFetchService
from congress.client.congress import Congress
from congress.config import CongressConfig
from congress.exceptions import NoCongressApiKeyException
from congress.members.interface import ICongressMemberRepository
from congress.members.service import CongressMemberRepository
from congress.transformation.interface import \
    ICongressDataTransformationService
from congress.transformation.service import CongressDataTransformationService

transformer = CongressDataTransformationService()


def getCongress(congressNum: int) -> Congress:
    """
    Returns a Congress client object for the given congress

    Args:
        congressNum (int): what number congress (e.g., 116)

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
    container.register(ICongressApiFetchService, CongressApiFetchService)
    container.register(ICongressMemberRepository, CongressMemberRepository)

    container.register(Congress)

    return cast(Congress, container.resolve(Congress))
