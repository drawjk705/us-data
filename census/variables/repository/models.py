from abc import ABC, abstractmethod
from typing import Generic, ItemsView, KeysView, List, TypeVar, ValuesView
from census.utils.cleanVariableName import cleanVariableName
from census.variables.models import Group, GroupCode, GroupVariable

ValueType = TypeVar("ValueType")
ItemType = TypeVar("ItemType")


class ICodeSet(ABC, Generic[ItemType, ValueType]):
    def __init__(self, *items: ItemType) -> None:
        for item in items:
            self.add(item)

    @abstractmethod
    def add(self, item: ItemType):
        pass

    def __len__(self) -> int:
        return len(self.__dict__)

    def names(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[ValueType]:
        return self.__dict__.values()

    def items(self) -> ItemsView[str, ValueType]:
        return self.__dict__.items()

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            return False

        if len(o) != len(self):
            return False

        for k, v in self.items():
            if not hasattr(o, k):
                return False
            if v != getattr(o, k):
                return False

        return True

    def __ne__(self, o: object) -> bool:
        return not self == o


class VariableSet(ICodeSet[GroupVariable, GroupVariable]):
    def add(self, item: GroupVariable):
        cleanedVarName = f"{item.cleanedName}_{item.groupCode}"

        self.__dict__.update({cleanedVarName: item})


class GroupSet(ICodeSet[Group, GroupCode]):
    def add(self, item: Group):
        cleanedGroupName = cleanVariableName(item.description)
        if cleanedGroupName in self.__dict__:
            cleanedGroupName += f"_{item.code}"
        self.__dict__.update({cleanedGroupName: item.code})
