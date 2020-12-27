from api.supportedVariableExtraction.models.GeographyItem import GeographyItem
from api.getDataBase import getDataBase
from api.supportedVariableExtraction.models import GeographyResponse
from models import SurveyType
from typing import List, Dict, Any, Set


def getSupportedGeographies(year: int, surveyType: SurveyType = SurveyType.ACS1) -> List[str]:
    geogRes = getDataBase(
        year, surveyType, route='geography.json')

    return __parseSupportedGeographies(geogRes)


def __parseSupportedGeographies(supportedGeosResponse: Any) -> Dict[str, Set[GeographyItem]]:
    geogRes = GeographyResponse(**supportedGeosResponse)
    supportedGeographies: Dict[str, Set[GeographyItem]] = {}

    for fip in geogRes.fips:
        varName = fip.name
        requirements = fip.requires or []
        wildcards = fip.wildcard or []
        nonWildcardableRequirements = list(
            filter(lambda req: req not in wildcards, fip.requires))

        withAllCodes = GeographyItem(
            forClause=f'{varName}:CODE',
            inClauses=[f'{requirement}:CODE' for requirement in requirements]
        )

        withWithCardForVar = GeographyItem(
            forClause=f'{varName}:*',
            inClauses=[
                f'{requirement}:CODE' for requirement in nonWildcardableRequirements]
        )

        withWildCardedRequirements = GeographyItem(
            forClause=f'{varName}:*',
            inClauses=[f'{requirement}:CODE' for requirement in nonWildcardableRequirements] + [
                f'{wildcard}:*' for wildcard in wildcards]
        )

        supportedGeographies[varName] = {
            withAllCodes,
            withWithCardForVar,
            withWildCardedRequirements}

    return supportedGeographies
