from models.DatasetType import DatasetType
from api.supportedVariableExtraction.models.GeographyItem import GeographyClauses, GeographyItem
from api.getData_Base import getData_Base
from api.supportedVariableExtraction.models import GeographyResponse
from models import SurveyType
from typing import Dict, Any, OrderedDict, Set


def getSupportedGeographies(year: int,
                            datasetType: DatasetType = DatasetType.ACS,
                            surveyType: SurveyType = SurveyType.ACS1) -> Dict[str, Set[GeographyItem]]:

    geogRes = getData_Base(year,
                           datasetType=datasetType,
                           surveyType=surveyType,
                           route='/geography.json')

    return __parseSupportedGeographies(geogRes)


def __parseSupportedGeographies(supportedGeosResponse: Any) -> OrderedDict[str, GeographyItem]:
    geogRes = GeographyResponse(**supportedGeosResponse)
    supportedGeographies: Dict[str, Set[GeographyItem]] = {}

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
