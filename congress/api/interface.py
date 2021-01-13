from abc import ABC, abstractmethod
from congress.api.models import Representative, Senator
from typing import List


class ICongressApiFetchService(ABC):
    """
    Calls ProPublica API to get basic
    info on congressional leaders
    """

    @abstractmethod
    def getRepresentatives(self) -> List[Representative]:
        ...

    @abstractmethod
    def getSenators(self) -> List[Senator]:
        pass
