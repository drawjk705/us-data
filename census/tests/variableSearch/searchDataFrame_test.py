import pandas
from typing import Tuple
from unittest.mock import MagicMock
from census.variableSearch.searchDataFrame import VariableSearchService
from tests.serviceTestFixtures import ServiceTestFixture


class TestVariableSearchService(ServiceTestFixture[VariableSearchService]):
    serviceType = VariableSearchService

    def test_searchGroups(self):
        (variableStorage,) = self._getDependencies()

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

    def _getDependencies(self) -> Tuple[MagicMock, ...]:
        return (self._dependencies["variableStorage"],)
