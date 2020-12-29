from api.ApiConfig import ApiConfig
from models import GeoDomain
from typing import Any, List
from api.utils import fetchData_Base


def fetchGeographyCodes(apiConfig: ApiConfig,
                        forDomain: GeoDomain,
                        inDomains: List[GeoDomain] = []) -> Any:

    forClause = f'for={forDomain}'
    inClauses = '&in='.join([str(parent) for parent in inDomains])

    querystring = f'?get=NAME&{forClause}'
    if len(inDomains):
        querystring += f'&in={inClauses}'

    return fetchData_Base(apiConfig, route=querystring)
