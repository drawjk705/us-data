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
    def parse_group_variables(self, group_variables: Any) -> List[GroupVariable]:
        if len(group_variables) == 0:
            return []

        variables: List[GroupVariable] = []
        for varCode, varData in group_variables["variables"].items():
            groupVar = GroupVariable.from_json(varCode, varData)
            variables.append(groupVar)

        return variables

    @timer
    def parse_supported_geographies(
        self,
        supported_geos_response: Any,
    ) -> OrderedDict[str, GeographyItem]:

        supported_geographies: Dict[str, GeographyItem] = {}

        if len(supported_geos_response) == 0:
            return OrderedDict(supported_geographies)

        fips = [
            GeographyResponseItem.from_json(fip)
            for fip in supported_geos_response["fips"]
        ]

        for fip in fips:
            varName = fip.name
            requirements = fip.requires or []
            wildcards = fip.wildcard or []
            nonWildcardableRequirements = list(
                filter(lambda req: req not in wildcards, fip.requires)
            )

            withAllCodes = GeographyClauseSet.makeSet(
                for_clause=f"{varName}:CODE",
                in_clauses=[f"{requirement}:CODE" for requirement in requirements],
            )

            withWithCardForVar = GeographyClauseSet.makeSet(
                for_clause=f"{varName}:*",
                in_clauses=[
                    f"{requirement}:CODE" for requirement in nonWildcardableRequirements
                ],
            )

            withWildCardedRequirements = GeographyClauseSet.makeSet(
                for_clause=f"{varName}:*",
                in_clauses=[
                    f"{requirement}:CODE" for requirement in nonWildcardableRequirements
                ]
                + [f"{wildcard}:*" for wildcard in wildcards],
            )

            supported_geographies[varName] = GeographyItem.makeItem(
                name=varName,
                hierarchy=fip.geoLevelDisplay,
                clauses=[withAllCodes, withWithCardForVar, withWildCardedRequirements],
            )

        return OrderedDict(
            sorted(supported_geographies.items(), key=lambda t: t[1].hierarchy)
        )

    @timer
    def parse_groups(
        self, groups_res: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Group]:

        if len(groups_res) == 0:
            return {}

        return {
            Group.from_json(group).code: Group.from_json(group)
            for group in groups_res["groups"]
        }
