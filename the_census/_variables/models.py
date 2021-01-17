# from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, NewType

from the_census._utils.cleanVariableName import cleanVariableName

VariableCode = NewType("VariableCode", str)
GroupCode = NewType("GroupCode", str)


@dataclass(frozen=True)
class Group:
    """
    DTO for the group retrieved from the API
    """

    code: GroupCode
    description: str
    variables: str = field(default="")
    cleanedName: str = field(default="")

    @classmethod
    def fromJson(cls, jsonDict: Dict[str, str]):
        code = jsonDict["name"]
        description = jsonDict["description"]
        variables = jsonDict.get("variables") or ""

        return cls(
            GroupCode(code), description, variables, cleanVariableName(description)
        )

    @classmethod
    def fromDfRecord(cls, record: Dict[str, Any]):
        return cls(
            GroupCode(record["code"]),
            record["description"],
            cleanedName=record["cleanedName"],
        )


@dataclass
class GroupVariable:
    """
    DTO for a variable retrieved from the API
    """

    code: VariableCode
    groupCode: GroupCode
    groupConcept: str
    name: str
    limit: int = field(default=0)
    predicateOnly: bool = field(default=False)
    predicateType: Literal["string", "int", "float"] = field(default="string")
    cleanedName: str = field(default="")

    @classmethod
    def fromJson(cls, code: str, jsonData: Dict[Any, Any]):
        groupCode = jsonData["group"]
        groupConcept = jsonData["concept"]
        label = jsonData["label"]
        limit = jsonData["limit"]
        predicateOnly = jsonData["predicateOnly"]
        predicateType = jsonData["predicateType"]
        cleanedName = cleanVariableName(label)

        return cls(
            VariableCode(code),
            groupCode,
            groupConcept,
            label,
            limit,
            predicateOnly,
            predicateType,
            cleanedName,
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
            record["cleanedName"],
        )

    def __hash__(self) -> int:
        return hash(self.code)

    # def __repr__(self) -> str:
    #     return self.__dict__.__repr__()

    # def __str__(self) -> str:
    #     return self.__repr__()
