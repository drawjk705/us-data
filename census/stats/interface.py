from abc import ABC, abstractmethod
from census.variables.models import VariableCode
from census.models import GeoDomain

from typing import Generic, List, TypeVar


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