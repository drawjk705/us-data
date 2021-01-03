# from dataclasses import dataclass
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, NewType


VariableCode = NewType("VariableCode", str)
GroupCode = NewType("GroupCode", str)


@dataclass
class Group:
    code: GroupCode
    description: str
    variables: str

    def __init__(
        self,
        code: str = "",
        description: str = "",
        variables: str = "",
    ) -> None:
        self.code = GroupCode(code)
        self.description = description
        self.variables = variables

    @classmethod
    def fromJson(cls, jsonDict: Dict[str, str]):
        code = jsonDict["name"]
        description = jsonDict["description"]
        variables = jsonDict["variables"]

        return cls(code, description, variables)

    @classmethod
    def fromDfRecord(cls, record: Dict[str, Any]):
        return cls(GroupCode(record["code"]), record["description"])

    def __hash__(self) -> int:
        return hash(self.code)


@dataclass
class GroupVariable:
    code: VariableCode
    groupCode: GroupCode
    groupConcept: str
    name: str
    limit: int
    predicateOnly: bool
    predicateType: Literal["string", "int", "float"]

    @classmethod
    def fromJson(cls, code: str, jsonData: Dict[Any, Any]):
        groupCode = jsonData["group"]
        groupConcept = jsonData["concept"]
        label = jsonData["label"]
        limit = jsonData["limit"]
        predicateOnly = jsonData["predicateOnly"]
        predicateType = jsonData["predicateType"]

        return cls(
            VariableCode(code),
            groupCode,
            groupConcept,
            label,
            limit,
            predicateOnly,
            predicateType,
        )

    @classmethod
    def fromDfRecord(cls, record: Dict[str, Any]):
        return cls(
            VariableCode(record["code"]),
            GroupCode(record["groupCode"]),
            record["groupConcept"],
            record["name"],
            record["limit"],
            record["predicateOnly"],
            record["predicateType"],
        )

    def __hash__(self) -> int:
        return hash(self.code)
