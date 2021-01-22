# from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, NewType

from the_census._utils.clean_variable_name import clean_variable_name

VariableCode = NewType("VariableCode", str)
GroupCode = NewType("group_code", str)


@dataclass(frozen=True)
class Group:
    """
    DTO for the group retrieved from the API
    """

    code: GroupCode
    description: str
    variables: str = field(default="")
    cleaned_name: str = field(default="")

    @classmethod
    def from_json(cls, jsonDict: Dict[str, str]):
        code = jsonDict.get("name", "")
        description = jsonDict.get("description", "")
        variables = jsonDict.get("variables", "")

        return cls(
            GroupCode(code), description, variables, clean_variable_name(description)
        )

    @classmethod
    def from_df_record(cls, record: Dict[str, Any]):
        return cls(
            GroupCode(record["code"]),
            record["description"],
            cleaned_name=record["cleaned_name"],
        )


@dataclass
class GroupVariable:
    """
    DTO for a variable retrieved from the API
    """

    code: VariableCode
    group_code: GroupCode
    group_concept: str
    name: str
    limit: int = field(default=0)
    predicate_only: bool = field(default=False)
    predicate_type: Literal["string", "int", "float"] = field(default="string")
    cleaned_name: str = field(default="")

    @classmethod
    def from_json(cls, code: str, jsonData: Dict[Any, Any]):
        group_code = jsonData.get("group", "")
        group_concept = jsonData.get("concept", "")
        label = jsonData.get("label", "")
        limit = jsonData.get("limit", 0)
        predicate_only = jsonData.get("predicateOnly", False)
        predicate_type = jsonData.get("predicateType", "string")
        cleaned_name = clean_variable_name(label)

        return cls(
            VariableCode(code),
            GroupCode(group_code),
            group_concept,
            label,
            limit,
            predicate_only,
            predicate_type,
            cleaned_name,
        )

    @classmethod
    def from_df_record(cls, record: Dict[str, Any]):
        return cls(
            VariableCode(record["code"]),
            GroupCode(record["group_code"]),
            record["group_concept"],
            record["name"],
            record["limit"],
            record["predicate_only"],
            record["predicate_type"],
            record["cleaned_name"],
        )

    def __hash__(self) -> int:
        return hash(self.code)
