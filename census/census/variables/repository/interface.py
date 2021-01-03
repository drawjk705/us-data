from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from census.models import GeoDomain
from census.variables.models import CodeSet, TGroupCode, TVariableCode

T = TypeVar("T")


class IVariableRepository(ABC, Generic[T]):
    # these will be useful for jupyter
    variableCodes: CodeSet[TVariableCode]
    groupCodes: CodeSet[TGroupCode]

    @abstractmethod
    def getGroups(self) -> T:
        pass

    @abstractmethod
    def getSupportedGeographies(self) -> T:
        pass

    @abstractmethod
    def getGeographyCodes(self, forDomain: GeoDomain, inDomains: List[GeoDomain]) -> T:
        pass

    @abstractmethod
    def getVariablesByGroup(self, groups: List[TGroupCode]) -> T:
        pass

    @abstractmethod
    def getAllVariables(self) -> T:
        pass
