from abc import ABC, abstractmethod
from census.variables.models import VariableCode
from census.models import GeoDomain

from typing import Generic, List, TypeVar


_T = TypeVar("_T")


class ICensusStatisticsService(ABC, Generic[_T]):
    @abstractmethod
    def getStats(
        self,
        variablesToQuery: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
        replaceColumnHeaders: bool = False,
    ) -> _T:
        pass