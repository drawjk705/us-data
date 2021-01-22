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
        logging_factory: ILoggerFactory,
    ) -> None:
        self._url = API_URL_FORMAT.format(config.year, config.dataset, config.survey)
        self._parser = parser
        self._config = config
        self._logger = logging_factory.getLogger(__name__)

    def healthcheck(self) -> None:
        res = requests.get(self._url + ".json")  # type: ignore

        if res.status_code in [404, 400]:
            msg = f"Data does not exist for dataset={self._config.dataset}; survey={self._config.survey}; year={self._config.year}"

            self._logger.exception(msg)

            raise CensusDoesNotExistException(msg)

        self._logger.debug("healthcheck OK")

    @timer
    def geography_codes(
        self, for_domain: GeoDomain, in_domains: List[GeoDomain] = []
    ) -> Any:

        for_clause = f"for={for_domain}"
        in_clauses = "&in=".join([str(parent) for parent in in_domains])

        querystring = f"?get=NAME&{for_clause}"
        if len(in_domains):
            querystring += f"&in={in_clauses}"  # type: ignore

        uri_querystring: str = requote_uri(querystring)

        return self._fetch(route=uri_querystring)

    @timer
    def group_data(self) -> Dict[str, Group]:
        groups_res: Dict[str, List[Dict[str, str]]] = self._fetch(route="/groups.json")

        return self._parser.parse_groups(groups_res)

    @timer
    def supported_geographies(self) -> OrderedDict[str, GeographyItem]:
        geogRes = self._fetch(route="/geography.json")

        return self._parser.parse_supported_geographies(geogRes)

    @timer
    def variables_for_group(self, group: str) -> List[GroupVariable]:
        res = self._fetch(route=f"/groups/{group}.json")

        return self._parser.parse_group_variables(res)

    @timer
    def all_variables(self) -> List[GroupVariable]:
        res = self._fetch("/variables.json")

        return self._parser.parse_group_variables(res)

    @timer
    def stats(
        self,
        variables_codes: List[VariableCode],
        for_domain: GeoDomain,
        in_domains: List[GeoDomain] = [],
    ) -> Generator[List[List[str]], None, None]:

        # we need the minus 1 since we're also querying name
        for codes in chunk(variables_codes, MAX_QUERY_SIZE - 1):
            code_str = ",".join(codes)
            var_str = "get=NAME" + f",{code_str}" if len(code_str) > 0 else ""

            domainStr = "for=" + str(for_domain)
            in_domainstr = "&".join([f"in={domain}" for domain in in_domains])

            if len(in_domainstr) > 0:
                domainStr += "&"  # type: ignore
                domainStr += in_domainstr  # type: ignore

            route = f"?{var_str}&{domainStr}"

            uri_route: str = requote_uri(route)

            # not doing any serializing here, because this is a bit more
            # complicated (we need to convert the stats to the appropriate
            # data types, [e.g., int, float] further up when we're working
            # with dataFrames; there's no real good way to do it down here)

            yield self._fetch(uri_route)

    def _fetch(self, route: str = "") -> Any:
        ampersand_or_question_mark = "&" if "?" in route else "?"
        url = (
            self._url
            + route
            + ampersand_or_question_mark
            + "key="
            + self._config.api_key
        )
        res = requests.get(url)  # type: ignore

        if res.status_code in [400, 404]:
            msg = f"Could not make query for route `{route}`"
            self._logger.exception(msg)
            raise InvalidQueryException(msg)

        if res.status_code == 204:  # no content
            msg = f"Received no content for query for route {route}"
            self._logger.info(msg)

            return []

        return res.json()  # type: ignore
