from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from the_census._variables.models import GroupCode
from the_census._variables.repository.models import GroupSet, VariableSet

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
    def get_groups(self) -> T:
        ...

    @abstractmethod
    def get_variables_by_group(self, *groups: GroupCode) -> T:
        ...

    @abstractmethod
    def get_all_variables(self) -> T:
        ...

    @property
    def variables(self) -> VariableSet:
        return self._variables

    @property
    def groups(self) -> GroupSet:
        return self._groups
