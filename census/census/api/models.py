from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass(frozen=True)
class GeographyClauses:
    forClause: str = ""
    inClauses: List[str] = field(default_factory=list)


@dataclass
class GeographyItem:
    name: str
    hierarchy: str
    clauses: Set[GeographyClauses] = field(default_factory=set)

    def __init__(
        self, name: str, hierarchy: str, clauses: List[GeographyClauses]
    ) -> None:
        self.name = name
        self.hierarchy = hierarchy
        self.clauses = set(clauses)


@dataclass
class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str] = field(default_factory=list)
    wildcard: List[str] = field(default_factory=list)
    optionalWithWCFor: str = ""

    def __init__(self, jsonRes: Any) -> None:
        self.__dict__ = jsonRes


@dataclass
class GeographyResponse:
    fips: List[GeographyResponseItem] = field(default_factory=list)

    def __init__(self, fips: List[dict], **_) -> None:  # type: ignore
        for fip in fips:
            self.fips.append(GeographyResponseItem(fip))  # type: ignore


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