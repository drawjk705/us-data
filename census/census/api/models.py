from census.utils.unique import getUnique
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


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
