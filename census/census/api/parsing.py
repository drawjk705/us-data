from typing import Any, Dict, List, OrderedDict
from census.api.models import (
    GeographyClauseSet,
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
    """
    parse a supported geographies response from the census API, e.g.:

    ```
        {
            "default": [
                {
                    "isDefault": "true"
                }
            ],
            "fips": [
                {
                    "name": "state",
                    "geoLevelDisplay": "040",
                    "referenceDate": "2019-01-01"
                },
                {
                    "name": "county",
                    "geoLevelDisplay": "050",
                    "referenceDate": "2019-01-01",
                    "requires": [
                        "state"
                    ],
                    "wildcard": [
                        "state"
                    ],
                    "optionalWithWCFor": "state"
                },
                {
                    "name": "principal city (or part)",
                    "geoLevelDisplay": "312",
                    "referenceDate": "2019-01-01",
                    "requires": [
                        "metropolitan statistical area/micropolitan statistical area",
                        "state (or part)"
                    ]
                },
            ]
        }
    ```

    Args:
        supportedGeosResponse (Any)

    Returns:
        OrderedDict[str, GeographyItem]: mapping the geography title to its name and code
    """

    geogRes = GeographyResponse(fips=supportedGeosResponse["fips"])
    supportedGeographies: Dict[str, GeographyItem] = {}

    for fip in geogRes.fips:
        varName = fip.name
        requirements = fip.requires or []
        wildcards = fip.wildcard or []
        nonWildcardableRequirements = list(
            filter(lambda req: req not in wildcards, fip.requires)
        )

        withAllCodes = GeographyClauseSet(
            forClause=f"{varName}:CODE",
            inClauses=tuple([f"{requirement}:CODE" for requirement in requirements]),
        )

        withWithCardForVar = GeographyClauseSet(
            forClause=f"{varName}:*",
            inClauses=tuple(
                [f"{requirement}:CODE" for requirement in nonWildcardableRequirements]
            ),
        )

        withWildCardedRequirements = GeographyClauseSet(
            forClause=f"{varName}:*",
            inClauses=tuple(
                [f"{requirement}:CODE" for requirement in nonWildcardableRequirements]
                + [f"{wildcard}:*" for wildcard in wildcards]
            ),
        )

        clauses = tuple({withAllCodes, withWithCardForVar, withWildCardedRequirements})

        supportedGeographies[varName] = GeographyItem(
            name=varName,
            hierarchy=fip.geoLevelDisplay,
            clauses=clauses,
        )

    return OrderedDict(
        sorted(supportedGeographies.items(), key=lambda t: t[1].hierarchy)
    )


def parseGroups(groupsRes: Dict[str, List[Dict[str, str]]]) -> Dict[str, Group]:
    return {Group(group).name: Group(group) for group in groupsRes["groups"]}
