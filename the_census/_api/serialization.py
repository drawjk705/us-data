from collections import OrderedDict
from typing import Any, Dict, List

from the_census._api.interface import ICensusApiSerializationService
from the_census._api.models import (
    GeographyClauseSet,
    GeographyItem,
    GeographyResponseItem,
)
from the_census._utils.timer import timer
from the_census._variables.models import Group, GroupVariable


class ApiSerializationService(ICensusApiSerializationService):
    @timer
    def parseGroupVariables(self, groupVariables: Any) -> List[GroupVariable]:
        variables: List[GroupVariable] = []
        for varCode, varData in groupVariables["variables"].items():
            groupVar = GroupVariable.fromJson(varCode, varData)
            variables.append(groupVar)

        return variables

    @timer
    def parseSupportedGeographies(
        self,
        supportedGeosResponse: Any,
    ) -> OrderedDict[str, GeographyItem]:

        fips = [
            GeographyResponseItem.fromJson(fip) for fip in supportedGeosResponse["fips"]
        ]

        supportedGeographies: Dict[str, GeographyItem] = {}

        for fip in fips:
            varName = fip.name
            requirements = fip.requires or []
            wildcards = fip.wildcard or []
            nonWildcardableRequirements = list(
                filter(lambda req: req not in wildcards, fip.requires)
            )

            withAllCodes = GeographyClauseSet.makeSet(
                forClause=f"{varName}:CODE",
                inClauses=[f"{requirement}:CODE" for requirement in requirements],
            )

            withWithCardForVar = GeographyClauseSet.makeSet(
                forClause=f"{varName}:*",
                inClauses=[
                    f"{requirement}:CODE" for requirement in nonWildcardableRequirements
                ],
            )

            withWildCardedRequirements = GeographyClauseSet.makeSet(
                forClause=f"{varName}:*",
                inClauses=[
                    f"{requirement}:CODE" for requirement in nonWildcardableRequirements
                ]
                + [f"{wildcard}:*" for wildcard in wildcards],
            )

            supportedGeographies[varName] = GeographyItem.makeItem(
                name=varName,
                hierarchy=fip.geoLevelDisplay,
                clauses=[withAllCodes, withWithCardForVar, withWildCardedRequirements],
            )

        return OrderedDict(
            sorted(supportedGeographies.items(), key=lambda t: t[1].hierarchy)
        )

    @timer
    def parseGroups(
        self, groupsRes: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Group]:
        return {
            Group.fromJson(group).code: Group.fromJson(group)
            for group in groupsRes["groups"]
        }
