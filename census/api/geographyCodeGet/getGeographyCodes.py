from api.ApiConfig import ApiConfig
from api.models.Domain import Domain
from typing import Any, List
from api import getData_Base


def getGeographyCodes(apiConfig: ApiConfig,
                      domain: Domain,
                      parentDomains: List[Domain] = []) -> Any:

    forClause = f'for={domain}'
    inClauses = '&in='.join([str(parent) for parent in parentDomains])

    querystring = f'?{forClause}'
    if len(parentDomains):
        querystring += f'&in={inClauses}'

    return getData_Base(apiConfig, route=querystring)
