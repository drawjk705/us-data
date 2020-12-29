from api.ApiConfig import ApiConfig
from api.models import Domain
from typing import Any, List
from api.utils import getData_Base


def fetchGeographyCodes(apiConfig: ApiConfig,
                        forDomain: Domain,
                        inDomains: List[Domain] = []) -> Any:

    forClause = f'for={forDomain}'
    inClauses = '&in='.join([str(parent) for parent in inDomains])

    querystring = f'?get=NAME&{forClause}'
    if len(inDomains):
        querystring += f'&in={inClauses}'

    return getData_Base(apiConfig, route=querystring)
