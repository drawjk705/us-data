from api.getDataBase import getDataBase
from api.supportedVariableExtraction.models import GeographyResponse
from models import SurveyType
from typing import OrderedDict, List, Any
from collections import OrderedDict


def getSupportedGeographies(year: int, surveyType: SurveyType = SurveyType.ACS1) -> List[str]:
    geogRes = getDataBase(
        year, surveyType, route='geography.json')

    return __parseSupportedGeographies(geogRes)


def __parseSupportedGeographies(supportedGeosResponse: Any) -> List[OrderedDict[str, str]]:
    geogRes = GeographyResponse(**supportedGeosResponse)
    supportedGeographies: List[OrderedDict[str, str]] = []

    for fip in geogRes.fips:
        varName = fip.name
        requirements = fip.requires or []
        wildcards = fip.wildcard or []

        if not len(requirements) and not len(wildcards):
            for suffix in ['*', 'CODE']:
                supportedGeographies.append(
                    OrderedDict({'for': f'{varName}:{suffix}'}))
        if len(requirements):
            requirementsDict = {
                'in': [
                    f'{requirement}:CODE'
                ] for requirement in requirements
            }

            supportedGeographies.append(
                OrderedDict({'for': f'{varName}:CODE', 'in': requirementsDict}))

    return supportedGeographies
