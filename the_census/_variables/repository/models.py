from abc import ABC, abstractmethod
from typing import Generic, ItemsView, KeysView, TypeVar, ValuesView

from the_census._variables.models import Group, GroupCode, GroupVariable

ValueType = TypeVar("ValueType")
ItemType = TypeVar("ItemType")


class ICodeSet(ABC, Generic[ItemType, ValueType]):
    def __init__(self, *items: ItemType) -> None:
        self.add(*items)

    @abstractmethod
    def add(self, *items: ItemType):
        ...

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
    def add(self, *items: GroupVariable):
        filteredItems = [item for item in items if item not in self.values()]

        entries = {
            f"{item.cleanedName}_{item.groupCode}": item for item in filteredItems
        }

        self.__dict__.update(entries)


class GroupSet(ICodeSet[Group, GroupCode]):
    def add(self, *items: Group):
        itemNames = [item.cleanedName for item in items]

        for item in items:
            if item.code in self.values():
                continue

            cleanedNameFreq = len([1 for name in itemNames if item.cleanedName == name])

            if cleanedNameFreq > 1 or item.cleanedName in self.__dict__:
                self.__dict__.update({f"{item.cleanedName}_{item.code}": item.code})
            else:
                self.__dict__.update({item.cleanedName: item.code})
