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
    def test_getStats_passesCorrectValuesToTransformer(self):
        apiRes = [1, 2, 3]
        apiGet = self.mocker.patch.object(
            self._service._api, "stats", return_value=apiRes
        )
        self.mocker.patch.object(
            self._service._variableRepo, "variables", variablesInRepo
        )
        variablesToQuery = [
            var1.code,
            var2.code,
            var3.code,
        ]
        forDomain = GeoDomain("state")
        inDomains = [GeoDomain("us")]
        expectedTypeConversions: Dict[str, Any] = dict(var1=int, var2=float)

        self._service.getStats(variablesToQuery, forDomain, inDomains)

        apiGet.assert_called_once_with(variablesToQuery, forDomain, inDomains)
        self.castMock(self._service._transformer.stats).assert_called_once_with(
            apiRes, variablesToQuery, expectedTypeConversions
        )
