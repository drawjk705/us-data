from dataclasses import dataclass, field
from typing import Dict, List, Tuple, cast

from the_census._utils.unique import getUnique


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


@dataclass(frozen=True)
class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str]
    wildcard: List[str]
    optionalWithWCFor: str = field(default="")

    @classmethod
    def fromJson(cls, jsonRes: Dict[str, str]):
        return cls(
            jsonRes.get("name", ""),
            jsonRes.get("geoLevelDisplay", ""),
            jsonRes.get("referenceDate", ""),
            cast(List[str], jsonRes.get("requires", [])),
            cast(List[str], jsonRes.get("wildcard", [])),
            jsonRes.get("optionalWithWCFor", ""),
        )
