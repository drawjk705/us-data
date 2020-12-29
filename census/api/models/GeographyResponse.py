from typing import List, Any


class GeographyResponseItem:
    name: str
    geoLevelDisplay: str
    referenceData: str
    requires: List[str] = []
    wildcard: List[str] = []
    optionalWithWCFor: str = ''

    def __init__(self, jsonRes: Any) -> None:
        self.__dict__ = jsonRes


class GeographyResponse:
    fips: List[GeographyResponseItem] = []

    def __init__(self, fips: List[dict], **_) -> None:
        for fip in fips:
            self.fips.append(GeographyResponseItem(fip))
