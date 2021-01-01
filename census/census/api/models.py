from census.variableStorage.models import TGroupCode, TVariableCode
from census.utils.unique import getUnique
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Tuple


@dataclass(frozen=True)
class GeographyClauseSet:
    forClause: str
    inClauses: Tuple[str]

    @classmethod
    def makeSet(cls, forClause: str, inClauses: List[str]):
        return cls(forClause, tuple(getUnique(inClauses)))

    def __repr__(self) -> str:
        return "\n".join([self.forClause] + list(self.inClauses))

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class GeographyItem:
    name: str
    hierarchy: str
    clauses: Tuple[GeographyClauseSet, ...]

    @classmethod
    def makeItem(cls, name: str, hierarchy: str, clauses: List[GeographyClauseSet]):
        return cls(name, hierarchy, tuple(getUnique(clauses)))

    def __repr__(self) -> str:
        rep = self.name + " - " + self.hierarchy + "\n------\n"

        rep += "\n--\n".join([str(clause) for clause in self.clauses])

        return rep

    def __str__(self) -> str:
        return self.__repr__()


class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str] = []
    wildcard: List[str] = []
    optionalWithWCFor: str

    def __init__(self, jsonRes: Any) -> None:
        self.__dict__ = jsonRes


class GeographyResponse:
    fips: List[GeographyResponseItem] = []

    def __init__(self, fips: List[Dict[Any, Any]], **_) -> None:
        for fip in fips:
            self.fips.append(GeographyResponseItem(fip))


@dataclass
class Group:
    code: TGroupCode
    description: str
    variables: str

    def __init__(
        self,
        code: str = "",
        description: str = "",
        variables: str = "",
    ) -> None:
        self.code = TGroupCode(code)
        self.description = description
        self.variables = variables

    @classmethod
    def fromJson(cls, jsonDict: Dict[str, str]):
        code = jsonDict["name"]
        description = jsonDict["description"]
        variables = jsonDict["variables"]

        return cls(code, description, variables)


@dataclass
class GroupVariable:
    code: TVariableCode
    groupCode: TGroupCode
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
            TVariableCode(code),
            groupCode,
            groupConcept,
            label,
            limit,
            predicateOnly,
            predicateType,
        )
