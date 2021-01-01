from census.api.interface import IApiFetchService, IApiSerializationService
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


class ApiFetchService(IApiFetchService):
    _url: str
    _parser: IApiSerializationService

    def __init__(self, config: Config, parser: IApiSerializationService) -> None:
        self.__url = API_URL_FORMAT.format(
            config.year, config.datasetType.value, config.surveyType.value
        )
        self._parser = parser

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

        return self._parser.parseGroups(groupsRes)

    def supportedGeographies(self) -> OrderedDict[str, GeographyItem]:

        geogRes = self.__fetch(route="/geography.json")

        return self._parser.parseSupportedGeographies(geogRes)

    def variablesForGroup(self, group: str) -> List[GroupVariable]:
        res = self.__fetch(route=f"/groups/{group}.json")

        return self._parser.parseVariableData(res)

    def stats(
        self,
        variables: List[GroupVariable],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain],
    ):
        varStr = "NAME" + ",".join([variable.code for variable in variables])

        domainStr = "for=" + str(forDomain)
        inDomainStr = "&".join([f"in={domain}" for domain in inDomains])

        if len(inDomainStr) == 0:
            domainStr += "&"
            domainStr += inDomainStr

        route = f"{varStr}?{domainStr}"

        res = self.__fetch(route)

    def __fetch(self, route: str = "") -> Any:
        url = self.__url + route
        return requests.get(url).json()  # type: ignore
