from typing import Any, Dict

import pytest

from tests.service_test_fixtures import ServiceTestFixture
from the_census._exceptions import EmptyRepositoryException
from the_census._geographies.models import GeoDomain
from the_census._stats.service import CensusStatisticsService
from the_census._variables.models import GroupCode, GroupVariable, VariableCode

# pyright: reportPrivateUsage=false

var1 = GroupVariable(
    code=VariableCode("var1"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 1",
    limit=1,
    predicate_only=False,
    predicate_type="int",
    cleaned_name="cleanedName1",
)
var2 = GroupVariable(
    code=VariableCode("var2"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 2",
    limit=1,
    predicate_only=False,
    predicate_type="float",
    cleaned_name="cleanedName2",
)
var3 = GroupVariable(
    code=VariableCode("var3"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 3",
    limit=1,
    predicate_only=False,
    predicate_type="string",
    cleaned_name="cleanedName3",
)
var4 = GroupVariable(
    code=VariableCode("var4"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 4",
    limit=1,
    predicate_only=False,
    predicate_type="string",
    cleaned_name="cleanedName4",
)

variables_in_repo: Dict[str, GroupVariable] = dict(
    var1=var1, var2=var2, var3=var3, var4=var4
)


class TestStatsAsDataFrame(ServiceTestFixture[CensusStatisticsService]):
    def test_get_stats(self):

        apiGet = self.mocker.patch.object(
            self._service._api, "stats", return_value=iter([[1, 2], [3]])
        )
        variables_to_query = [
            var1.code,
            var2.code,
            var3.code,
        ]
        for_domain = GeoDomain("state")
        in_domains = [GeoDomain("us")]
        expected_column_mapping: Dict[str, int] = dict(map=1)
        expectedTypeMapping: Dict[str, Any] = dict(map=int)

        self.mocker.patch.object(
            self._service,
            "_get_variable_names_and_type_conversions",
            return_value=(expected_column_mapping, expectedTypeMapping),
        )

        geoRepoRetval = []
        self.mocker.patch.object(
            self._service._geo_repo,
            "get_supported_geographies",
            return_value=geoRepoRetval,
        )

        self._service.get_stats(variables_to_query, for_domain, *in_domains)

        apiGet.assert_called_once_with(variables_to_query, for_domain, in_domains)
        self.cast_mock(self._service._transformer.stats).assert_called_once_with(
            [[1, 2], [3]],
            expectedTypeMapping,
            [for_domain] + in_domains,
            expected_column_mapping,
            geoRepoRetval,
        )

    def test_get_stats_with_empty_variable_repo(self):
        variables_to_query = [var1.code]
        self.mocker.patch.object(self._service._variable_repo, "variables", dict())

        with pytest.raises(
            EmptyRepositoryException,
            match="Queried 1 variables, but found only 0 in repository",
        ):
            self._service.get_stats(variables_to_query, GeoDomain("place"))

    def test_get_variable_names_and_type_conversions_for_unique_names(self):
        variables_to_query = {
            var1.code,
            var2.code,
            var3.code,
        }

        self.mocker.patch.object(
            self._service._variable_repo, "variables", variables_in_repo
        )

        (
            columnMapping,
            typeMapping,
        ) = self._service._get_variable_names_and_type_conversions(variables_to_query)

        assert columnMapping == {
            "var1": "cleanedName1",
            "var2": "cleanedName2",
            "var3": "cleanedName3",
        }
        assert typeMapping == {"var1": float, "var2": float}

    def test_get_variable_names_and_type_conversions_for_duplicate_names(self):
        variable_with_duplicate_name = GroupVariable(
            code=VariableCode("var5"),
            group_code=GroupCode("g2"),
            group_concept="concept 3",
            limit=0,
            predicate_type="string",
            predicate_only=False,
            name=var1.name,
            cleaned_name=var1.cleaned_name,
        )
        self.mocker.patch.object(
            self._service._variable_repo,
            "variables",
            dict(variables_in_repo, var5=variable_with_duplicate_name),
        )
        variables_to_query = {
            var1.code,
            var2.code,
            var3.code,
            variable_with_duplicate_name.code,
        }

        (
            column_mapping,
            type_mapping,
        ) = self._service._get_variable_names_and_type_conversions(variables_to_query)

        assert column_mapping == {
            "var1": "cleanedName1_g1",
            "var2": "cleanedName2_g1",
            "var3": "cleanedName3_g1",
            "var5": "cleanedName1_g2",
        }
        assert type_mapping == {"var1": float, "var2": float}
