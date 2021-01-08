from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, ItemsView, KeysView, TypeVar, ValuesView, cast
from census.utils.cleanVariableName import cleanVariableName
from census.variables.models import Group, GroupVariable, VariableCode

_T = TypeVar("_T")


@dataclass(frozen=True)
class _CodeOrCleanedName:
    code: VariableCode
    name: str


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

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.__repr__()


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
        if cleanedGroupName in self.__dict__:
            cleanedGroupName += f"_{item.code}"
        self.__dict__.update({cleanedGroupName: item})


class VariableNameToCodeSet(ICodeSet[GroupVariable]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: GroupVariable):
        cleanedName = cleanVariableName(item.name)

        self.__dict__.update({cleanedName: _CodeOrCleanedName(item.code, cleanedName)})

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.__repr__()


class GroupToVarsMapping(ICodeSet[GroupVariable]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, item: GroupVariable):
        groupName = cleanVariableName(item.groupConcept)
        if groupName not in self.__dict__:
            self.__dict__[groupName] = VariableNameToCodeSet()
        cast(VariableNameToCodeSet, self.__dict__[groupName]).add(item)
