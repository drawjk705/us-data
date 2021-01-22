from dataclasses import dataclass, field
from typing import Dict, List, Tuple, cast

from the_census._utils.unique import get_unique


@dataclass(frozen=True)
class GeographyClauseSet:
    for_clause: str
    in_clauses: Tuple[str, ...]

    @classmethod
    def makeSet(cls, for_clause: str, in_clauses: List[str]):
        return cls(for_clause, tuple(get_unique(in_clauses)))

    def __repr__(self) -> str:
        return "\n".join([self.for_clause] + list(self.in_clauses))

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class GeographyItem:
    name: str
    hierarchy: str
    clauses: Tuple[GeographyClauseSet, ...]

    @classmethod
    def makeItem(cls, name: str, hierarchy: str, clauses: List[GeographyClauseSet]):
        return cls(name, hierarchy, tuple(get_unique(clauses)))


@dataclass(frozen=True)
class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str]
    wildcard: List[str]
    optionalWithWCFor: str = field(default="")

    @classmethod
    def from_json(cls, jsonRes: Dict[str, str]):
        return cls(
            jsonRes.get("name", ""),
            jsonRes.get("geoLevelDisplay", ""),
            jsonRes.get("referenceDate", ""),
            cast(List[str], jsonRes.get("requires", [])),
            cast(List[str], jsonRes.get("wildcard", [])),
            jsonRes.get("optionalWithWCFor", ""),
        )
