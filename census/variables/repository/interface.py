from abc import ABC, abstractmethod
from census.variables.repository.models import (
    GroupSet,
    VariableSet,
)
from typing import Generic, List, TypeVar

from census.models import GeoDomain
from census.variables.models import GroupCode

T = TypeVar("T")


class IVariableRepository(ABC, Generic[T]):
    """
    Gets and stores all variable metadata (i.e., codes,
    meanings of variables, etc.)
    """

    # these are collections of all variables/groups
    # that have been pulled from the API so far
    _variables: VariableSet
    _groups: GroupSet

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

    @property
    def variables(self) -> VariableSet:
        return self._variables

    @property
    def groups(self) -> GroupSet:
        return self._groups
