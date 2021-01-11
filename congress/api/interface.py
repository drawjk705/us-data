from abc import ABC, abstractmethod
from congress.api.models import Representative, Senator
from typing import List


class ICongressApiFetchService(ABC):
    @abstractmethod
    def getRepresentatives(self) -> List[Representative]:
        pass

    @abstractmethod
    def getSenators(self) -> List[Senator]:
        pass