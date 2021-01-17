from collections import OrderedDict
from logging import Logger
from typing import Any, Dict, Generator, List

import requests
from requests.utils import requote_uri

from the_census._api.interface import (
    ICensusApiFetchService,
    ICensusApiSerializationService,
)
from the_census._api.models import GeographyItem
from the_census._config import Config
from the_census._exceptions import CensusDoesNotExistException, InvalidQueryException
from the_census._geographies.models import GeoDomain
from the_census._utils.chunk import chunk
from the_census._utils.log.factory import ILoggerFactory
from the_census._utils.timer import timer
from the_census._variables.models import Group, GroupVariable, VariableCode

# we can query only 50 variables at a time, max
MAX_QUERY_SIZE = 50
API_URL_FORMAT = "https://api.census.gov/data/{0}/{1}/{2}"


class CensusApiFetchService(ICensusApiFetchService):
    _url: str
    _parser: ICensusApiSerializationService
    _config: Config
    _logger: Logger

    def __init__(
        self,
        config: Config,
        parser: ICensusApiSerializationService,
        loggingFactory: ILoggerFactory,
    ) -> None:
        self._url = API_URL_FORMAT.format(
            config.year, config.datasetType, config.surveyType
        )
        self._parser = parser
        self._config = config
        self._logger = loggingFactory.getLogger(__name__)

    def healthCheck(self) -> None:
        res = requests.get(self._url + ".json")  # type: ignore

        if res.status_code in [404, 400]:
            msg = f"Data does not exist for dataset={self._config.datasetType}; survey={self._config.surveyType}; year={self._config.year}"

            self._logger.exception(msg)

            raise CensusDoesNotExistException(msg)

        self._logger.debug("healthCheck OK")

    @timer
    def geographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> Any:

        forClause = f"for={forDomain}"
        inClauses = "&in=".join([str(parent) for parent in inDomains])

        querystring = f"?get=NAME&{forClause}"
        if len(inDomains):
            querystring += f"&in={inClauses}"  # type: ignore

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
        for codes in chunk(variablesCodes, MAX_QUERY_SIZE - 1):
            codeStr = ",".join(codes)
            varStr = "get=NAME" + f",{codeStr}" if len(codeStr) > 0 else ""

            domainStr = "for=" + str(forDomain)
            inDomainStr = "&".join([f"in={domain}" for domain in inDomains])

            if len(inDomainStr) > 0:
                domainStr += "&"  # type: ignore
                domainStr += inDomainStr  # type: ignore

            route = f"?{varStr}&{domainStr}"

            uriRoute: str = requote_uri(route)

            # not doing any serializing here, because this is a bit more
            # complicated (we need to convert the stats to the appropriate
            # data types, [e.g., int, float] further up when we're working
            # with dataFrames; there's no real good way to do it down here)

            yield self.__fetch(uriRoute)

    def __fetch(self, route: str = "") -> Any:
        ampersandOrQuestionMark = "&" if "?" in route else "?"
        url = self._url + route + ampersandOrQuestionMark + "key=" + self._config.apiKey
        res = requests.get(url)  # type: ignore
        if res.status_code in [400, 404]:
            msg = f"Could not make query for route `{route}`"
            self._logger.exception(msg)
            raise InvalidQueryException(msg)

        return res.json()  # type: ignore
