from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from census.geographies.models import GeoDomain
from census.variables.models import VariableCode

_T = TypeVar("_T")


class ICensusStatisticsService(ABC, Generic[_T]):
    """
    Pulls and massages statistical data from the
    Census API
    """

    @abstractmethod
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        *inDomains: GeoDomain,
    ) -> _T:
        pass
