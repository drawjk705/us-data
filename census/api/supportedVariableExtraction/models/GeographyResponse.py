
from typing import List, Optional, Dict


class GeographyItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: Optional[List[str]]
    wildcard: Optional[List[str]]
    optionalWithWcFor: Optional[str]

    def __init__(self, jsonRes: dict) -> None:
        self.__dict__ = jsonRes


class GeographyResponse:
    default: List[Dict[str, str]] = []
    fips: List[GeographyItem] = []

    def __init__(self, fips: List[GeographyItem], default: Dict[str, str]) -> None:
        for fip in fips:
            self.fips.append(GeographyItem(fip))
        self.default = default
