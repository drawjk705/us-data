from census.utils.unique import getUnique
from dataclasses import dataclass
from typing import Any, List, Tuple


@dataclass(frozen=True)
class GeographyClauseSet:
    forClause: str
    inClauses: Tuple[str, ...]

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


class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str] = []
    wildcard: List[str] = []
    optionalWithWCFor: str

    def __init__(self, jsonRes: Any) -> None:
        self.__dict__ = jsonRes

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __str__(self) -> str:
        return self.__repr__()
