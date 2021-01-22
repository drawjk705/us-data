import pandas

from tests.service_test_fixtures import ServiceTestFixture
from the_census._variables.models import GroupCode
from the_census._variables.search.service import VariableSearchService

# pyright: reportPrivateUsage=false


class TestVariableSearchService(ServiceTestFixture[VariableSearchService]):
    def test_search_groups(self):
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
        self.mocker.patch.object(
            self._service._variable_repository, "get_groups", return_value=foundDf
        )

        expectedRes = pandas.DataFrame({"description": ["banana", "elephant"]})

        res = self._service.search_groups("an")

        assert res.to_dict() == expectedRes.to_dict()

    def test_search_all_variables(self):
        repoVariables = pandas.DataFrame(
            [dict(name="banana"), dict(name="apple"), dict(name="elephant")]
        )
        self.mocker.patch.object(
            self._service._variable_repository,
            "get_all_variables",
            return_value=repoVariables,
        )

        res = self._service.search_variables("an")

        assert res.to_dict("records") == pandas.DataFrame(
            [dict(name="banana"), dict(name="elephant")]
        ).to_dict("records")

    def test_search_variables_in_groups(self):
        repoVariables = pandas.DataFrame(
            [dict(name="banana"), dict(name="apple"), dict(name="elephant")]
        )
        self.mocker.patch.object(
            self._service._variable_repository,
            "get_variables_by_group",
            return_value=repoVariables,
        )

        res = self._service.search_variables("an", GroupCode("abc"))

        assert res.to_dict("records") == pandas.DataFrame(
            [dict(name="banana"), dict(name="elephant")]
        ).to_dict("records")
