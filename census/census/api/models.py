from census.utils.unique import getUnique
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from functools import total_ordering


@dataclass(frozen=True)
@total_ordering
class GeographyClauseSet:
    forClause: str
    inClauses: Tuple[str]

    @classmethod
    def makeSet(cls, forClause: str, inClauses: List[str]):
        return cls(forClause, tuple(sorted(getUnique(inClauses))))

    def __repr__(self) -> str:
        return "\n".join([self.forClause] + list(self.inClauses))

    def __str__(self) -> str:
        return self.__repr__()

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise Exception(f"cannot compare {type(o)} with {type(self)}")

        return self.__repr__() < o.__repr__()


@dataclass(frozen=True)
class GeographyItem:
    name: str
    hierarchy: str
    clauses: Tuple[GeographyClauseSet, ...]

    @classmethod
    def makeItem(cls, name: str, hierarchy: str, clauses: List[GeographyClauseSet]):
        return cls(name, hierarchy, tuple(sorted(getUnique(clauses))))

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

    def __init__(
        self,
        jsonRes: Dict[str, str] = {},
        name: str = "",
        description: str = "",
        variables: str = "",
    ) -> None:
        if len(jsonRes):
            self.__dict__ = jsonRes
        else:
            self.name = name
            self.description = description
            self.variables = variables


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