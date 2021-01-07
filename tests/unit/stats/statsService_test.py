from tests.utils import shuffledCases
import pytest
from census.models import GeoDomain
from typing import Any, Dict
from census.variables.models import GroupCode, GroupVariable, VariableCode
from tests.serviceTestFixtures import ServiceTestFixture
from census.stats.service import CensusStatisticsService

# pyright: reportPrivateUsage=false

var1 = GroupVariable(
    code=VariableCode("var1"),
    groupCode=GroupCode("g1"),
    groupConcept="concept1",
    name="name 1",
    limit=1,
    predicateOnly=False,
    predicateType="int",
)
var2 = GroupVariable(
    code=VariableCode("var2"),
    groupCode=GroupCode("g1"),
    groupConcept="concept1",
    name="name 2",
    limit=1,
    predicateOnly=False,
    predicateType="float",
)
var3 = GroupVariable(
    code=VariableCode("var3"),
    groupCode=GroupCode("g1"),
    groupConcept="concept1",
    name="name 3",
    limit=1,
    predicateOnly=False,
    predicateType="string",
)
var4 = GroupVariable(
    code=VariableCode("var4"),
    groupCode=GroupCode("g1"),
    groupConcept="concept1",
    name="name 4",
    limit=1,
    predicateOnly=False,
    predicateType="string",
)

variablesInRepo: Dict[str, GroupVariable] = dict(
    var1=var1, var2=var2, var3=var3, var4=var4
)


class TestStatsAsDataFrame(ServiceTestFixture[CensusStatisticsService]):
    @pytest.mark.parametrize(*shuffledCases(shouldReplaceColumnHeaders=[True, False]))
    def test_getStats_passesCorrectValuesToTransformer(
        self, shouldReplaceColumnHeaders: bool
    ):
        apiGet = self.mocker.patch.object(
            self._service._api, "stats", return_value=iter([[1, 2], [3]])
        )
        self.mocker.patch.object(
            self._service._config, "replaceColumnHeaders", shouldReplaceColumnHeaders
        )
        variablesToQuery = [
            var1.code,
            var2.code,
            var3.code,
        ]
        forDomain = GeoDomain("state")
        inDomains = [GeoDomain("us")]
        expectedColumnMapping: Dict[str, int] = dict(map=1)
        expectedTypeMapping: Dict[str, Any] = dict(map=int)

        self.mocker.patch.object(
            self._service,
            "_getVariableNamesAndTypeConversions",
            return_value=(expectedColumnMapping, expectedTypeMapping),
        )

        self._service.getStats(variablesToQuery, forDomain, *inDomains)

        apiGet.assert_called_once_with(variablesToQuery, forDomain, inDomains)
        self.castMock(self._service._transformer.stats).assert_called_once_with(
            [[1, 2], [3]],
            expectedTypeMapping,
            [forDomain] + inDomains,
            columnHeaders=expectedColumnMapping if shouldReplaceColumnHeaders else None,
        )

    def test_getVariableNamesAndTypeConversions_givenUniqueNames(self):
        variablesToQuery = {
            var1.code,
            var2.code,
            var3.code,
        }
        self.mocker.patch("census.stats.service.cleanVariableName", lambda x: x)  # type: ignore
        self.mocker.patch.object(
            self._service._variableRepo, "variables", variablesInRepo
        )

        columnMapping, typeMapping = self._service._getVariableNamesAndTypeConversions(
            variablesToQuery
        )

        assert columnMapping == {"var1": "name 1", "var2": "name 2", "var3": "name 3"}
        assert typeMapping == {"var1": int, "var2": float}

    def test_getVariableNamesAndTypeConversions_givenDuplicateNamesBetweenGroups(self):
        variableWithDuplicateName = GroupVariable(
            code=VariableCode("var5"),
            groupCode=GroupCode("g2"),
            groupConcept="concept 3",
            limit=0,
            predicateType="string",
            predicateOnly=False,
            name=var1.name,
        )
        variablesToQuery = {
            var1.code,
            var2.code,
            var3.code,
            variableWithDuplicateName.code,
        }
        self.mocker.patch("census.stats.service.cleanVariableName", lambda x: x)  # type: ignore
        self.mocker.patch.object(
            self._service._variableRepo,
            "variables",
            dict(variablesInRepo, var5=variableWithDuplicateName),
        )

        columnMapping, typeMapping = self._service._getVariableNamesAndTypeConversions(
            variablesToQuery
        )

        assert columnMapping == {
            "var1": "name 1_g1",
            "var2": "name 2_g1",
            "var3": "name 3_g1",
            "var5": "name 1_g2",
        }
        assert typeMapping == {"var1": int, "var2": float}
