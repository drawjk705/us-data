from typing import Any, Dict

import pytest

from tests.serviceTestFixtures import ServiceTestFixture
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
    cleaned_name="cleaned_name1",
)
var2 = GroupVariable(
    code=VariableCode("var2"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 2",
    limit=1,
    predicate_only=False,
    predicate_type="float",
    cleaned_name="cleaned_name2",
)
var3 = GroupVariable(
    code=VariableCode("var3"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 3",
    limit=1,
    predicate_only=False,
    predicate_type="string",
    cleaned_name="cleaned_name3",
)
var4 = GroupVariable(
    code=VariableCode("var4"),
    group_code=GroupCode("g1"),
    group_concept="concept1",
    name="name 4",
    limit=1,
    predicate_only=False,
    predicate_type="string",
    cleaned_name="cleaned_name4",
)

variablesInRepo: Dict[str, GroupVariable] = dict(
    var1=var1, var2=var2, var3=var3, var4=var4
)


class TestStatsAsDataFrame(ServiceTestFixture[CensusStatisticsService]):
    def test_get_stats_passesCorrectValuesToTransformer(self):
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
        expectedColumnMapping: Dict[str, int] = dict(map=1)
        expectedTypeMapping: Dict[str, Any] = dict(map=int)

        self.mocker.patch.object(
            self._service,
            "_getVariableNamesAndtype_conversions",
            return_value=(expectedColumnMapping, expectedTypeMapping),
        )

        geoRepoRetval = []
        self.mocker.patch.object(
            self._service._geoRepo,
            "get_supported_geographies",
            return_value=geoRepoRetval,
        )

        self._service.get_stats(variables_to_query, for_domain, *in_domains)

        apiGet.assert_called_once_with(variables_to_query, for_domain, in_domains)
        self.castMock(self._service._transformer.stats).assert_called_once_with(
            [[1, 2], [3]],
            expectedTypeMapping,
            [for_domain] + in_domains,
            expectedColumnMapping,
            geoRepoRetval,
        )

    def test_getVariableNamesAndtype_conversions_givenEmptyRepo_throws(self):
        variables_to_query = [var1.code]
        self.mocker.patch.object(self._service._variableRepo, "variables", dict())

        with pytest.raises(
            EmptyRepositoryException,
            match="Queried 1 variables, but found only 0 in repository",
        ):
            self._service.get_stats(variables_to_query, GeoDomain("place"))

    def test_getVariableNamesAndtype_conversions_givenUniqueNames(self):
        variables_to_query = {
            var1.code,
            var2.code,
            var3.code,
        }

        self.mocker.patch.object(
            self._service._variableRepo, "variables", variablesInRepo
        )

        columnMapping, typeMapping = self._service._getVariableNamesAndtype_conversions(
            variables_to_query
        )

        assert columnMapping == {
            "var1": "cleaned_name1",
            "var2": "cleaned_name2",
            "var3": "cleaned_name3",
        }
        assert typeMapping == {"var1": float, "var2": float}

    def test_getVariableNamesAndtype_conversions_givenDuplicateNamesBetweenGroups(self):
        variableWithDuplicateName = GroupVariable(
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
            self._service._variableRepo,
            "variables",
            dict(variablesInRepo, var5=variableWithDuplicateName),
        )
        variables_to_query = {
            var1.code,
            var2.code,
            var3.code,
            variableWithDuplicateName.code,
        }

        columnMapping, typeMapping = self._service._getVariableNamesAndtype_conversions(
            variables_to_query
        )

        assert columnMapping == {
            "var1": "cleaned_name1_g1",
            "var2": "cleaned_name2_g1",
            "var3": "cleaned_name3_g1",
            "var5": "cleaned_name1_g2",
        }
        assert typeMapping == {"var1": float, "var2": float}
