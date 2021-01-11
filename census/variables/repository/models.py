from abc import ABC, abstractmethod
from typing import Generic, ItemsView, KeysView, TypeVar, ValuesView
from census.utils.cleanVariableName import cleanVariableName
from census.variables.models import Group, GroupCode, GroupVariable, VariableCode

CodeType = TypeVar("CodeType")
ItemType = TypeVar("ItemType")


class ICodeSet(ABC, Generic[CodeType, ItemType]):
    @abstractmethod
    def add(self, item: ItemType):
        pass

    def __len__(self) -> int:
        return len(self.__dict__)

    def names(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[CodeType]:
        return self.__dict__.values()

    def items(self) -> ItemsView[str, CodeType]:
        return self.__dict__.items()

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.__repr__()


class VariableSet(ICodeSet[VariableCode, GroupVariable]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: GroupVariable):
        cleanedVarName = f"{item.cleanedName}_{item.groupCode}"

        self.__dict__.update({cleanedVarName: item.code})


class GroupSet(ICodeSet[GroupCode, Group]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: Group):
        cleanedGroupName = cleanVariableName(item.description)
        if cleanedGroupName in self.__dict__:
            cleanedGroupName += f"_{item.code}"
        self.__dict__.update({cleanedGroupName: item.code})
