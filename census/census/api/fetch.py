from census.api.serialization import ApiSerializationService
from census.config import Config
from collections import OrderedDict
from typing import Any, Dict, List

import requests

from census.api.constants import API_URL_FORMAT
from census.api.models import (
    GeographyItem,
    Group,
    GroupVariable,
)
from census.models import GeoDomain


class ApiFetchService:
    __url: str
    __parser: ApiSerializationService

    def __init__(self, config: Config, parser: ApiSerializationService) -> None:
        self.__url = API_URL_FORMAT.format(
            config.year, config.datasetType.value, config.surveyType.value
        )
        self.__parser = parser

    def geographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> Any:

        forClause = f"for={forDomain}"
        inClauses = "&in=".join([str(parent) for parent in inDomains])

        querystring = f"?get=NAME&{forClause}"
        if len(inDomains):
            querystring += f"&in={inClauses}"

        return self.__fetch(route=querystring)

    def groupData(self) -> Dict[str, Group]:
        groupsRes: Dict[str, List[Dict[str, str]]] = self.__fetch(route="/groups.json")

        return self.__parser.parseGroups(groupsRes)

    def supportedGeographies(self) -> OrderedDict[str, GeographyItem]:

        geogRes = self.__fetch(route="/geography.json")

        return self.__parser.parseSupportedGeographies(geogRes)

    def variables(self, group: str) -> List[GroupVariable]:
        res = self.__fetch(route=f"/groups/{group}.json")

        return self.__parser.parseVariableData(res)

    def __fetch(self, route: str = "") -> Any:
        url = self.__url + route
        return requests.get(url).json()  # type: ignore
