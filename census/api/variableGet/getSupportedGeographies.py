from api.ApiConfig import ApiConfig
from api.models.GeographyResponse import GeographyResponse
from api.models.GeographyItem import GeographyItem, GeographyClauses
from api.getData_Base import getData_Base
from typing import Dict, Any, OrderedDict


def getSupportedGeographies(apiConfig: ApiConfig) -> OrderedDict[str, GeographyItem]:

    geogRes = getData_Base(apiConfig, route='/geography.json')

    return __parseSupportedGeographies(geogRes)


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
