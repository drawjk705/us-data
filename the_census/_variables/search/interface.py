from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from the_census._variables.models import GroupCode

_T = TypeVar("_T")


class IVariableSearchService(ABC, Generic[_T]):
    """
    Handles searching through stored variables
    """

    @abstractmethod
    def search_groups(self, regex: str) -> _T:
        ...

    @abstractmethod
    def search_variables(
        self,
        regex: str,
        *in_groups: GroupCode,
    ) -> _T:
        ...
