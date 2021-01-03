# from dataclasses import dataclass
from dataclasses import dataclass
from typing import Any, Dict, Literal, NewType

from attr import field


VariableCode = NewType("VariableCode", str)
GroupCode = NewType("GroupCode", str)


@dataclass(frozen=True)
class Group:
    code: GroupCode
    description: str
    variables: str = field(default="")

    @classmethod
    def fromJson(cls, jsonDict: Dict[str, str]):
        code = jsonDict["name"]
        description = jsonDict["description"]
        variables = jsonDict["variables"]

        return cls(GroupCode(code), description, variables)

    @classmethod
    def fromDfRecord(cls, record: Dict[str, Any]):
        return cls(GroupCode(record["code"]), record["description"])


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
            record["concept"],
            record["name"],
            record["limit"],
            record["predicateOnly"],
            record["predicateType"],
        )

    def __hash__(self) -> int:
        return hash(self.code)
