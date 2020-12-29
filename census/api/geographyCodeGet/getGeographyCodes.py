from api.models.Domain import Domain
from typing import Dict, List
from api import getData_Base


def getGeographyCodes(domain: Domain,
                      parentDomains: List[Domain] = []) -> Dict[str, str]:

    forClause = f'for={domain}'
    inClauses = '&in='.join([str(parent) for parent in parentDomains])

    querystring = f'?{forClause}'
    if len(parentDomains):
        querystring += f'&in={inClauses}'

    return getData_Base()
