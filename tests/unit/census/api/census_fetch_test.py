from typing import List
from unittest.mock import MagicMock, call

import pytest
from callee import StartsWith, String

from tests.serviceTestFixtures import ApiServiceTestFixture
from tests.utils import MockRes
from us_data.census._api.fetch import CensusApiFetchService
from us_data.census._api.interface import ICensusApiSerializationService
from us_data.census._config import Config
from us_data.census._exceptions import (
    CensusDoesNotExistException,
    InvalidQueryException,
)
from us_data.census._geographies.models import GeoDomain
from us_data.census._variables.models import VariableCode

mockConfig = Config(year=2019, datasetType="acs", surveyType="acs1")


class ApiServiceWrapper(CensusApiFetchService):
    def __init__(self, parser: ICensusApiSerializationService) -> None:
        super().__init__(config=mockConfig, parser=parser, loggingFactory=MagicMock())


class TestApiFetchService(ApiServiceTestFixture[ApiServiceWrapper]):
    def test_fetch_givenStatusCodeNot200(self):
        self.requestsGetMock.return_value = MockRes(404)

        with pytest.raises(
            InvalidQueryException, match="Could not make query for route `/groups.json`"
        ):
            self._service.groupData()

    @pytest.mark.parametrize(
        ["domain", "parentDomains", "expectedRoute"],
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
    def test_geographyCodes(
        self,
        domain: GeoDomain,
        parentDomains: List[GeoDomain],
        expectedRoute: str,
    ):
        self._service.geographyCodes(domain, parentDomains)

        self.requestsGetMock.assert_called_once_with(
            String() & StartsWith(expectedRoute)
        )

    def test_groupData_callsFetch(self):
        self._service.groupData()

        self.requestsGetMock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/groups.json")
        )

    def test_supportedGeographies_callsFetch(self):
        self._service.supportedGeographies()

        self.requestsGetMock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/geography.json")
        )

    def test_variablesForGroup_callsFetch(self):
        group = "abc123"

        self._service.variablesForGroup(group)

        self.requestsGetMock.assert_called_with(
            String()
            & StartsWith(
                f"https://api.census.gov/data/2019/acs/acs1/groups/{group}.json"
            )
        )

    def test_stats_callsFetchInBatches(self):
        self.mocker.patch("us_data.census.api.fetch.MAX_QUERY_SIZE", 3)

        varCodes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        forDomain = GeoDomain("banana")
        inDomains = [GeoDomain("phone", "92")]

        for _ in self._service.stats(varCodes, forDomain, inDomains):
            ...
        assert self.requestsGetMock.call_args_list == [
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

    def test_allVariables(self):
        self._service.allVariables()

        self.requestsGetMock.assert_called_once_with(
            String()
            & StartsWith("https://api.census.gov/data/2019/acs/acs1/variables.json")
        )

    def test_stats_yieldsBatches(self):
        self.mocker.patch("us_data.census.api.fetch.MAX_QUERY_SIZE", 3)

        varCodes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        self.requestsGetMock.side_effect = [
            MockRes(200, [["header1", "header2"], ["a", "b"], ["c", "d"]]),
            MockRes(200, [["header1", "header2"], ["e", "f"], ["g", "h"]]),
        ]

        res = self._service.stats(varCodes, GeoDomain(""), [GeoDomain("")])

        assert next(res) == [["header1", "header2"], ["a", "b"], ["c", "d"]]
        assert next(res) == [["header1", "header2"], ["e", "f"], ["g", "h"]]

        with pytest.raises(StopIteration):
            next(res)

    def test_healthCheck_pass(self):
        self.requestsGetMock.return_value = MockRes(200)

        self._service.healthCheck()

        self.castMock(self._service._logger.debug).assert_called_once_with(
            "healthCheck OK"
        )

    def test_healthCheck_fail(self):
        self.requestsGetMock.return_value = MockRes(404)

        msg = "Data does not exist for dataset=acs; survey=acs1; year=2019"

        with pytest.raises(CensusDoesNotExistException, match=msg):
            self._service.healthCheck()

        self.castMock(self._service._logger.exception).assert_called_once_with(msg)
