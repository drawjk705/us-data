from requests.utils import requote_uri
from census.exceptions import CensusDoesNotExistException, InvalidQueryException
from census.utils.timer import timer
from census.variables.models import Group, GroupVariable, VariableCode
from census.utils.chunk import chunk
from census.api.interface import IApiFetchService, IApiSerializationService
from census.config import Config
from collections import OrderedDict
from typing import Any, Dict, Generator, List, cast
import logging
from tqdm.notebook import tqdm  # type: ignore

import requests

from census.api.models import GeographyItem
from census.models import GeoDomain

# we can query only 50 variables at a time, max
MAX_QUERY_SIZE = 50
API_URL_FORMAT = "https://api.census.gov/data/{0}/{1}/{2}"


class ApiFetchService(IApiFetchService):
    _url: str
    _parser: IApiSerializationService
    _config: Config

    def __init__(self, config: Config, parser: IApiSerializationService) -> None:
        self._url = API_URL_FORMAT.format(
            config.year, config.datasetType.value, config.surveyType.value
        )
        self._parser = parser
        self._config = config

    def healthCheck(self) -> None:
        res = requests.get(self._url + ".json")  # type: ignore

        if res.status_code in [404, 400]:
            msg = f"Data does not exist for dataset={self._config.datasetType.value}; survey={self._config.surveyType.value}; year={self._config.year}"

            logging.error(f"[ApiFetchService] - {msg}")

            raise CensusDoesNotExistException(msg)

        logging.debug("[ApiFetchService] - healthCheck OK")

    @timer
    def geographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> Any:

        forClause = f"for={forDomain}"
        inClauses = "&in=".join([str(parent) for parent in inDomains])

        querystring = f"?get=NAME&{forClause}"
        if len(inDomains):
            querystring += f"&in={inClauses}"

        uriQuerystring: str = requote_uri(querystring)

        return self.__fetch(route=uriQuerystring)

    @timer
    def groupData(self) -> Dict[str, Group]:
        groupsRes: Dict[str, List[Dict[str, str]]] = self.__fetch(route="/groups.json")

        return self._parser.parseGroups(groupsRes)

    @timer
    def supportedGeographies(self) -> OrderedDict[str, GeographyItem]:

        geogRes = self.__fetch(route="/geography.json")

        return self._parser.parseSupportedGeographies(geogRes)

    @timer
    def variablesForGroup(self, group: str) -> List[GroupVariable]:
        res = self.__fetch(route=f"/groups/{group}.json")

        return self._parser.parseGroupVariables(res)

    @timer
    def allVariables(self) -> List[GroupVariable]:
        res = self.__fetch("/variables.json")

        return self._parser.parseGroupVariables(res)

    @timer
    def stats(
        self,
        variablesCodes: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> Generator[List[List[str]], None, None]:

        # we need the minus 1 since we're also querying name
        for codes in tqdm(chunk(variablesCodes, MAX_QUERY_SIZE - 1)):
            codeStr = ",".join(cast(List[VariableCode], codes))
            varStr = "get=NAME" + f",{codeStr}" if len(codeStr) > 0 else ""

            domainStr = "for=" + str(forDomain)
            inDomainStr = "&".join([f"in={domain}" for domain in inDomains])

            if len(inDomainStr) > 0:
                domainStr += "&"
                domainStr += inDomainStr

            route = f"?{varStr}&{domainStr}"

            uriRoute: str = requote_uri(route)

            # not doing any serializing here, because this is a bit more
            # complicated (we need to convert the variables to the appropriate
            # data types further up when we're working with dataFrames; there's
            # no real good way to do it down here)

            yield self.__fetch(uriRoute)

    def __fetch(self, route: str = "") -> Any:
        url = self._url + route
        res = requests.get(url)  # type: ignore
        if res.status_code in [400, 404]:
            raise InvalidQueryException(f"Could not make query for route `{route}`")

        return res.json()  # type: ignore
