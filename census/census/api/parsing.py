from typing import Any, Dict, List, OrderedDict
from census.api.models import (
    GeographyClauses,
    GeographyItem,
    GeographyResponse,
    Group,
    GroupVariable,
)


def parseVariableData(variableData: Any) -> List[GroupVariable]:
    """parseVariableData

    Parses an API response for variable retrieval, e.g.:

    ```
      {
        "variables": {
            "B01001_047EA": {
                "label": "Annotation of Estimate!!Total:!!Female:!!75 to 79 years",
                "concept": "SEX BY AGE",
                "predicateType": "string",
                "group": "B01001",
                "limit": 0,
                "predicateOnly": true
            },
            "B01001_047MA": {
                "label": "Annotation of Margin of Error!!Total:!!Female:!!75 to 79 years",
                "concept": "SEX BY AGE",
                "predicateType": "string",
                "group": "B01001",
                "limit": 0,
                "predicateOnly": true
            }
        }
      },
    ```

    Args:
        variableData (Any): JSON response

    Returns:
        List[GroupVariable]:
    """

    variables: List[GroupVariable] = []
    for varCode, varData in variableData["variables"].items():
        groupVar = GroupVariable(varCode, varData)
        variables.append(groupVar)

    return variables


def parseSupportedGeographies(
    supportedGeosResponse: Any,
) -> OrderedDict[str, GeographyItem]:
    geogRes = GeographyResponse(**supportedGeosResponse)
    supportedGeographies: Dict[str, GeographyItem] = {}

    for fip in geogRes.fips:
        varName = fip.name
        requirements = fip.requires or []
        wildcards = fip.wildcard or []
        nonWildcardableRequirements = list(
            filter(lambda req: req not in wildcards, fip.requires)
        )

        withAllCodes = GeographyClauses(
            forClause=f"{varName}:CODE",
            inClauses=[f"{requirement}:CODE" for requirement in requirements],
        )

        withWithCardForVar = GeographyClauses(
            forClause=f"{varName}:*",
            inClauses=[
                f"{requirement}:CODE" for requirement in nonWildcardableRequirements
            ],
        )

        withWildCardedRequirements = GeographyClauses(
            forClause=f"{varName}:*",
            inClauses=[
                f"{requirement}:CODE" for requirement in nonWildcardableRequirements
            ]
            + [f"{wildcard}:*" for wildcard in wildcards],
        )

        supportedGeographies[varName] = GeographyItem(
            name=varName,
            hierarchy=fip.geoLevelDisplay,
            clauses=[withAllCodes, withWithCardForVar, withWildCardedRequirements],
        )

    return OrderedDict(
        sorted(supportedGeographies.items(), key=lambda t: t[1].hierarchy)
    )


def parseGroups(groupsRes: Dict[str, List[Dict[str, str]]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes["groups"]}
