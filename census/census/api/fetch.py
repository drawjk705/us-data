from census.variables.models import TVariableCode
from census.utils.chunk import chunk
from census.api.interface import IApiFetchService, IApiSerializationService
from census.config import Config
from collections import OrderedDict
from typing import Any, Dict, List

import requests

from census.api.constants import API_URL_FORMAT
from census.api.models import GeographyItem, Group, GroupVariable
from census.models import GeoDomain

# we can query only 50 variables at a time, max
MAX_QUERY_SIZE = 50


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

        return self._parser.parseGroupVariables(res)

    def stats(
        self,
        variablesCodes: List[TVariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain],
    ):
        res: List[List[str]] = []

        for i, codes in enumerate(chunk(variablesCodes, MAX_QUERY_SIZE)):
            codeStr = ",".join(codes)
            varStr = "get=NAME" + f",{codeStr}" if len(codeStr) > 0 else ""

            domainStr = "for=" + str(forDomain)
            inDomainStr = "&".join([f"in={domain}" for domain in inDomains])

            if len(inDomainStr) == 0:
                domainStr += "&"
                domainStr += inDomainStr

            route = f"?{varStr}&{domainStr}"

            resp = self.__fetch(route)

            if i > 0:
                res += resp[1:]
            else:
                res += resp

        # not doing any serializing here, because this is a bit more
        # complicated (we need to convert the variables to the appropriate
        # data types further up when we're working with dataFrames; there's
        # no real good way to do it down here)
        return res

    def __fetch(self, route: str = "") -> Any:
        url = self.__url + route
        return requests.get(url).json()  # type: ignore
