from census.variables.models import GroupCode
from typing import Generic, TypeVar
from abc import ABC, abstractmethod


_T = TypeVar("_T")


class IVariableSearchService(ABC, Generic[_T]):
    """
    Handles searching through stored variables
    """

    @abstractmethod
    def searchGroups(self, regex: str) -> _T:
        ...

    @abstractmethod
    def searchVariables(
        self,
        regex: str,
        *inGroups: GroupCode,
    ) -> _T:
        ...
