from abc import ABC, abstractmethod
from census.models import GeoDomain

from typing import Generic, List, TypeVar

from census.api.models import GroupVariable

_T = TypeVar("_T")


class ICensusStatisticsService(ABC, Generic[_T]):
    @abstractmethod
    def getStats(
        self,
        variablesToQuery: List[GroupVariable],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> _T:
        pass