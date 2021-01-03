from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar

from census.models import GeoDomain
from census.variables.models import Group, GroupVariable, GroupCode, VariableCode

T = TypeVar("T")


class IVariableRepository(ABC, Generic[T]):
    variables: Dict[VariableCode, GroupVariable]
    groups: Dict[GroupCode, Group]

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
    def getVariablesByGroup(self, groups: List[GroupCode]) -> T:
        pass

    @abstractmethod
    def getAllVariables(self) -> T:
        pass
