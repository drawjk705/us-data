
from typing import List, Dict


class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str] = []
    wildcard: List[str] = []
    optionalWithWCFor: str = ''

    def __init__(self, jsonRes: dict) -> None:
        self.__dict__ = jsonRes


class GeographyResponse:
    default: List[Dict[str, str]] = []
    fips: List[GeographyResponseItem] = []

    def __init__(self, fips: List[GeographyResponseItem], default: Dict[str, str]) -> None:
        for fip in fips:
            self.fips.append(GeographyResponseItem(fip))
        self.default = default
