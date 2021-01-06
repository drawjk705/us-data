from typing import ItemsView, KeysView, ValuesView
from census.utils.cleanVariableName import cleanVariableName
from census.variables.models import Group, GroupVariable


class VariableSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, variable: GroupVariable):
        cleanedVarName = cleanVariableName(variable.name)
        cleanedVarName += f"_{variable.groupCode}"

        self.__dict__.update({cleanedVarName: variable})

    def __len__(self) -> int:
        return len(self.__dict__)

    def names(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[GroupVariable]:
        return self.__dict__.values()

    def items(self) -> ItemsView[str, GroupVariable]:
        return self.__dict__.items()


class GroupSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, group: Group):
        cleanedGroupName = cleanVariableName(group.description)
        self.__dict__.update({cleanedGroupName: group})

    def __len__(self) -> int:
        return len(self.__dict__)

    def names(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[Group]:
        return self.__dict__.values()

    def items(self) -> ItemsView[str, Group]:
        return self.__dict__.items()