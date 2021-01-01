from census.variableStorage.models import TGroupCode
from typing import Generic, List, Literal, TypeVar
from abc import ABC, abstractmethod


_T = TypeVar("_T")


class IVariableSearchService(ABC, Generic[_T]):
    @abstractmethod
    def searchGroups(self, regex: str) -> _T:
        pass

    @abstractmethod
    def searchVariables(
        self,
        regex: str,
        searchBy: Literal["name", "concept"] = "name",
        inGroups: List[TGroupCode] = [],
    ) -> _T:
        pass
