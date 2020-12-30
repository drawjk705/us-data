from collections import OrderedDict
from typing import Any, Dict, List

import requests

from census.api import parsing
from census.api.ApiConfig import ApiConfig
from census.api.constants import API_URL_FORMAT
from census.api.models import (
    GeographyItem,
    Group,
    GroupVariable,
)
from census.models import GeoDomain


def geographyCodes(
    apiConfig: ApiConfig, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
) -> Any:

    forClause = f"for={forDomain}"
    inClauses = "&in=".join([str(parent) for parent in inDomains])

    querystring = f"?get=NAME&{forClause}"
    if len(inDomains):
        querystring += f"&in={inClauses}"

    return __fetchData_Base(apiConfig, route=querystring)


def groupData(apiConfig: ApiConfig) -> Dict[str, Group]:
    groupsRes: Dict[str, List[Dict[str, str]]] = __fetchData_Base(
        apiConfig, route="/groups.json"
    )

    return parsing.parseGroups(groupsRes)


def supportedGeographies(apiConfig: ApiConfig) -> OrderedDict[str, GeographyItem]:

    geogRes = __fetchData_Base(apiConfig, route="/geography.json")

    return parsing.parseSupportedGeographies(geogRes)


def variableData(group: str, apiConfig: ApiConfig) -> List[GroupVariable]:
    res = __fetchData_Base(apiConfig, route=f"/groups/{group}.json")

    return parsing.parseVariableData(res)


def __fetchData_Base(apiConfig: ApiConfig, route: str = "") -> Any:
    url = (
        API_URL_FORMAT.format(
            apiConfig.year, apiConfig.datasetType.value, apiConfig.surveyType.value
        )
        + route
    )
    return requests.get(url).json()  # type: ignore
