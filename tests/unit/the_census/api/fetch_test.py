from typing import List
from unittest.mock import MagicMock, call

import pytest
from callee import StartsWith, String

from tests.service_test_fixtures import ApiServiceTestFixture
from tests.utils import MockRes
from the_census._api.fetch import CensusApiFetchService
from the_census._api.interface import ICensusApiSerializationService
from the_census._config import Config
from the_census._exceptions import CensusDoesNotExistException, InvalidQueryException
from the_census._geographies.models import GeoDomain
from the_census._variables.models import VariableCode

mockConfig = Config(year=2019, dataset="acs", survey="acs1")


class ApiServiceWrapper(CensusApiFetchService):
    def __init__(self, parser: ICensusApiSerializationService) -> None:
        super().__init__(config=mockConfig, parser=parser, logging_factory=MagicMock())


class TestApiFetchService(ApiServiceTestFixture[ApiServiceWrapper]):
    def test_400_status_code(self):
        self.requests_get_mock.return_value = MockRes(404)

        with pytest.raises(
            InvalidQueryException, match="Could not make query for route `/groups.json`"
        ):
            self._service.group_data()

    def test_204_no_content(self):
        self.requests_get_mock.return_value = MockRes(204)

        res = self._service._fetch("anything")

        self._service._logger.info.assert_called_once_with(
            "Received no content for query for route anything"
        )
        assert res == []

    @pytest.mark.parametrize(
        ["domain", "parent_domains", "expected_route"],
        [
            (
                GeoDomain("state"),
                [GeoDomain("us")],
                "https://api.census.gov/data/2019/acs/acs1?get=NAME&for=state:*&in=us:*",
            ),
            (
                GeoDomain("county", "01"),
                [GeoDomain("state", "01")],
                "https://api.census.gov/data/2019/acs/acs1?get=NAME&for=county:01&in=state:01",
            ),
            (
                GeoDomain("county", "01"),
                [GeoDomain("state", "01"), GeoDomain("us")],
                "https://api.census.gov/data/2019/acs/acs1?get=NAME&for=county:01&in=state:01&in=us:*",
            ),
        ],
    )
    def test_geography_codes(
        self,
        domain: GeoDomain,
        parent_domains: List[GeoDomain],
        expected_route: str,
    ):
        self._service.geography_codes(domain, parent_domains)

        self.requests_get_mock.assert_called_once_with(
            String() & StartsWith(expected_route)
        )

    def test_group_data_calls_fetch(self):
        self._service.group_data()

        self.requests_get_mock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/groups.json")
        )

    def test_supported_geographies_calls_fetch(self):
        self._service.supported_geographies()

        self.requests_get_mock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/geography.json")
        )

    def test_variables_for_group_calls_fetch(self):
        group = "abc123"

        self._service.variables_for_group(group)

        self.requests_get_mock.assert_called_with(
            String()
            & StartsWith(
                f"https://api.census.gov/data/2019/acs/acs1/groups/{group}.json"
            )
        )

    def test_stats_calls_fetch_in_batches(self):
        self.mocker.patch("the_census._api.fetch.MAX_QUERY_SIZE", 3)

        var_codes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        for_domain = GeoDomain("banana")
        in_domains = [GeoDomain("phone", "92")]

        for _ in self._service.stats(var_codes, for_domain, in_domains):
            pass

        assert self.requests_get_mock.call_args_list == [
            call(
                String()
                & StartsWith(
                    "https://api.census.gov/data/2019/acs/acs1?get=NAME,1,2&for=banana:*&in=phone:92"
                )
            ),
            call(
                String()
                & StartsWith(
                    "https://api.census.gov/data/2019/acs/acs1?get=NAME,3,4&for=banana:*&in=phone:92"
                )
            ),
        ]

    def test_all_variables(self):
        self._service.all_variables()

        self.requests_get_mock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/variables.json")
        )

    def test_stats_yields_batches(self):
        self.mocker.patch("the_census._api.fetch.MAX_QUERY_SIZE", 3)

        var_codes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        self.requests_get_mock.side_effect = [
            MockRes(200, [["header1", "header2"], ["a", "b"], ["c", "d"]]),
            MockRes(200, [["header1", "header2"], ["e", "f"], ["g", "h"]]),
        ]

        res = self._service.stats(var_codes, GeoDomain(""), [GeoDomain("")])

        assert next(res) == [["header1", "header2"], ["a", "b"], ["c", "d"]]
        assert next(res) == [["header1", "header2"], ["e", "f"], ["g", "h"]]

        with pytest.raises(StopIteration):
            next(res)

    def test_healthcheck_pass(self):
        self.requests_get_mock.return_value = MockRes(200)

        self._service.healthcheck()

        self.cast_mock(self._service._logger.debug).assert_called_once_with(
            "healthcheck OK"
        )

    def test_healthcheck_fail(self):
        self.requests_get_mock.return_value = MockRes(404)

        msg = "Data does not exist for dataset=acs; survey=acs1; year=2019"

        with pytest.raises(CensusDoesNotExistException, match=msg):
            self._service.healthcheck()

        self.cast_mock(self._service._logger.exception).assert_called_once_with(msg)
