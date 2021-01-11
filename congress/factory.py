# pyright: reportUnknownMemberType=false

from congress.client.congress import Congress
from congress.members.service import CongressMemberRepository
from congress.members.interface import ICongressMemberRepository
from congress.api.fetch import CongressApiFetchService
from congress.api.interface import ICongressApiFetchService
from congress.transformation.interface import ICongressTransformationService
from congress.transformation.service import CongressTransformationService
from typing import cast
from congress.config import CongressConfig
import dotenv
import os
import punq

dotenvPath = dotenv.find_dotenv()
dotenv.load_dotenv(dotenvPath)  # type: ignore

transformer = CongressTransformationService()


def getCongress(congressNum: int) -> Congress:
    """
    Returns a Congress client object for the given congress

    Args:
        congressNum (int): what number congress (e.g., 116)

    Returns:
        Congress: client object
    """

    apiKey = cast(str, os.getenv("PROPUBLICA_CONG_KEY"))
    config = CongressConfig(congressNum, apiKey)

    container = punq.Container()

    container.register(ICongressTransformationService, instance=transformer)

    container.register(CongressConfig, instance=config)
    container.register(ICongressApiFetchService, CongressApiFetchService)
    container.register(ICongressMemberRepository, CongressMemberRepository)

    container.register(Congress)

    return cast(Congress, container.resolve(Congress))
