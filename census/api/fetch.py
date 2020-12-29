from typing import Any, Dict, List, OrderedDict

import requests

from api import ApiConfig
from api.ApiConfig import ApiConfig
from api.constants import API_URL_FORMAT
from api.models import (GeographyClauses, GeographyItem, GeographyResponse,
                        Group, GroupVariable)
from models import GeoDomain


def geographyCodes(apiConfig: ApiConfig,
                   forDomain: GeoDomain,
                   inDomains: List[GeoDomain] = []) -> Any:

    forClause = f'for={forDomain}'
    inClauses = '&in='.join([str(parent) for parent in inDomains])

    querystring = f'?get=NAME&{forClause}'
    if len(inDomains):
        querystring += f'&in={inClauses}'

    return __fetchData_Base(apiConfig, route=querystring)


def groupData(apiConfig: ApiConfig) -> Dict[str, Group]:
    groupsRes: Dict[str, List[Dict[str, str]]] = __fetchData_Base(
        apiConfig, route='/groups.json')

    return __parseGroups(groupsRes)


def supportedGeographiesData(apiConfig: ApiConfig) -> OrderedDict[str, GeographyItem]:

    geogRes = __fetchData_Base(apiConfig, route='/geography.json')

    return __parseSupportedGeographies(geogRes)


def variableData(group: str, apiConfig: ApiConfig) -> List[GroupVariable]:
    res = __fetchData_Base(apiConfig, route=f'/groups/{group}.json')

    return __parseVariableData(res)


def __parseVariableData(variableData: Any) -> List[GroupVariable]:
    variables = []
    for varCode, varData in variableData['variables'].items():
        groupVar = GroupVariable(code=varCode, jsonData=varData)
        variables.append(groupVar)

    return variables


def __parseSupportedGeographies(supportedGeosResponse: Any) -> OrderedDict[str, GeographyItem]:
    geogRes = GeographyResponse(**supportedGeosResponse)
    supportedGeographies: Dict[str, GeographyItem] = {}

    for fip in geogRes.fips:
        varName = fip.name
        requirements = fip.requires or []
        wildcards = fip.wildcard or []
        nonWildcardableRequirements = list(
            filter(lambda req: req not in wildcards, fip.requires))

        withAllCodes = GeographyClauses(
            forClause=f'{varName}:CODE',
            inClauses=[f'{requirement}:CODE' for requirement in requirements]
        )

        withWithCardForVar = GeographyClauses(
            forClause=f'{varName}:*',
            inClauses=[
                f'{requirement}:CODE' for requirement in nonWildcardableRequirements]
        )

        withWildCardedRequirements = GeographyClauses(
            forClause=f'{varName}:*',
            inClauses=[f'{requirement}:CODE' for requirement in nonWildcardableRequirements] + [
                f'{wildcard}:*' for wildcard in wildcards]
        )

        supportedGeographies[varName] = \
            GeographyItem(name=varName,
                          hierarchy=fip.geoLevelDisplay,
                          clauses={withAllCodes,
                                   withWithCardForVar,
                                   withWildCardedRequirements})

    return OrderedDict(sorted(supportedGeographies.items(), key=lambda t: t[1].hierarchy))


def __parseGroups(groupsRes: Dict[str, List[Dict[str, str]]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes['groups']}


def __fetchData_Base(apiConfig: ApiConfig,
                     route: str = '') -> Any:
    url = API_URL_FORMAT.format(
        apiConfig.year, apiConfig.datasetType.value, apiConfig.surveyType.value) + route
    return requests.get(url).json()  # type: ignore
