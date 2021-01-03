import pandas
from census.variables.search.service import VariableSearchService
from tests.serviceTestFixtures import ServiceTestFixture

# pyright: reportPrivateUsage=false


class TestVariableSearchService(ServiceTestFixture[VariableSearchService]):
    def test_searchGroups(self):
        variableStorage = self.castMock(self._service._variableRepository)
        foundDf = pandas.DataFrame(
            {
                "description": [
                    "apple",
                    "banana",
                    "carl",
                    "dog",
                    "elephant",
                    "fruit",
                    "giraffe",
                ]
            }
        )
        self.mocker.patch.object(variableStorage, "getGroups", return_value=foundDf)

        expectedRes = pandas.DataFrame({"description": ["banana", "elephant"]})

        res = self._service.searchGroups("an")

        assert res.to_dict() == expectedRes.to_dict()
