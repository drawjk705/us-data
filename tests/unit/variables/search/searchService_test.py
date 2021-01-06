from census.variables.models import GroupCode
import pandas
import pytest
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

    def test_searchVariables_givenBadSearchCriteria_throws(self):
        with pytest.raises(Exception) as e:
            self._service.searchVariables("", "banana")  # type: ignore

        assert str(e.value) == 'searchBy parameter must be "name" or "concept"'

    def test_searchVariables_inAllGroups(self):
        repoVariables = pandas.DataFrame(
            [dict(name="banana"), dict(name="apple"), dict(name="elephant")]
        )
        self.mocker.patch.object(
            self._service._variableRepository,
            "getAllVariables",
            return_value=repoVariables,
        )

        res = self._service.searchVariables("an", "name")

        assert res.to_dict("records") == pandas.DataFrame(
            [dict(name="banana"), dict(name="elephant")]
        ).to_dict("records")

    def test_searchVariables_inGroups(self):
        repoVariables = pandas.DataFrame(
            [dict(name="banana"), dict(name="apple"), dict(name="elephant")]
        )
        self.mocker.patch.object(
            self._service._variableRepository,
            "getVariablesByGroup",
            return_value=repoVariables,
        )

        res = self._service.searchVariables("an", "name", [GroupCode("abc")])

        assert res.to_dict("records") == pandas.DataFrame(
            [dict(name="banana"), dict(name="elephant")]
        ).to_dict("records")
