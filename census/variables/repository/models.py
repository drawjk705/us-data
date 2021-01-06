from abc import ABC, abstractmethod
from typing import Generic, ItemsView, KeysView, TypeVar, ValuesView
from census.utils.cleanVariableName import cleanVariableName
from census.variables.models import Group, GroupVariable

_T = TypeVar("_T")


class ICodeSet(ABC, Generic[_T]):
    @abstractmethod
    def add(self, item: _T):
        pass

    def __len__(self) -> int:
        return len(self.__dict__)

    def names(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[_T]:
        return self.__dict__.values()

    def items(self) -> ItemsView[str, _T]:
        return self.__dict__.items()


class VariableSet(ICodeSet[GroupVariable]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: GroupVariable):
        cleanedVarName = cleanVariableName(item.name)
        cleanedVarName += f"_{item.groupCode}"

        self.__dict__.update({cleanedVarName: item})


class GroupSet(ICodeSet[Group]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: Group):
        cleanedGroupName = cleanVariableName(item.description)
        self.__dict__.update({cleanedGroupName: item})
