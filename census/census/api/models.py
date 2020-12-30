from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class GeographyClauseSet:
    forClause: str
    inClauses: Tuple[str]

    def __repr__(self) -> str:
        return "\n".join([self.forClause] + list(self.inClauses))

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class GeographyItem:
    name: str
    hierarchy: str
    clauses: Tuple[GeographyClauseSet, ...]

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
    name: str
    description: str
    variables: str

    def __init__(self, jsonRes: Dict[str, str]) -> None:
        self.__dict__ = jsonRes


@dataclass
class GroupVariable:
    code: str
    __jsonData: Dict[Any, Any]

    groupCode: str = field(init=False)
    groupConcept: str = field(init=False)
    name: str = field(init=False)
    limit: int = field(init=False)
    predicateOnly: bool = field(init=False)
    predicateType: str = field(init=False)

    def __post_init__(self):
        self.groupCode = self.__jsonData["group"]
        self.groupConcept = self.__jsonData["concept"]
        self.name = self.__jsonData["label"]
        self.limit = self.__jsonData["limit"]
        self.predicateOnly = self.__jsonData["predicateOnly"]
        self.predicateType = self.__jsonData["predicateType"]