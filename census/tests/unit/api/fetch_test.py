from census.exceptions import CensusDoesNotExistException, InvalidQueryException
from pytest_mock.plugin import MockerFixture
from census.variables.models import VariableCode
from typing import Any, Collection, List
from unittest.mock import MagicMock, call
from census.config import Config
from census.api.interface import IApiSerializationService

import pytest
from census.api.fetch import ApiFetchService
from census.models import DatasetType, GeoDomain, SurveyType
from tests.serviceTestFixtures import ApiServiceTestFixture

mockConfig = Config(year=2019, datasetType=DatasetType.ACS, surveyType=SurveyType.ACS1)


@pytest.fixture
def logMock(mocker: MockerFixture):
    return mocker.patch("census.api.fetch.logging")


class MockRes:
    status_code: int
    content: Collection[Any]

    def __init__(self, status_code: int, content: Collection[Any] = {}) -> None:
        self.status_code = status_code
        self.content = content

    def json(self) -> Collection[Any]:
        return self.content


class ApiServiceWrapper(ApiFetchService):
    def __init__(self, parser: IApiSerializationService) -> None:
        super().__init__(config=mockConfig, parser=parser)


class TestApiFetchService(ApiServiceTestFixture[ApiServiceWrapper]):
    def test_fetch_givenStatusCodeNot200(self):
        self.mocker.patch.object(self.requestsMock, "get", return_value=MockRes(404))

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
                f"https://api.census.gov/data/2019/acs/acs1?get=NAME&for=county:01&in=state:01",
            ),
            (
                GeoDomain("county", "01"),
                [GeoDomain("state", "01"), GeoDomain("us")],
                f"https://api.census.gov/data/2019/acs/acs1?get=NAME&for=county:01&in=state:01&in=us:*",
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

        self.requestsMock.get.assert_called_once_with(expectedRoute)  # type: ignore

    def test_groupData_callsFetch(self):
        self._service.groupData()

        self.requestsMock.get.assert_called_once_with(  # type: ignore
            "https://api.census.gov/data/2019/acs/acs1/groups.json"
        )

    def test_supportedGeographies_callsFetch(self):
        self._service.supportedGeographies()

        self.requestsMock.get.assert_called_once_with(  # type: ignore
            "https://api.census.gov/data/2019/acs/acs1/geography.json"
        )

    def test_variablesForGroup_callsFetch(self):
        group = "abc123"

        self._service.variablesForGroup(group)

        self.requestsMock.get.assert_called_with(  # type: ignore
            f"https://api.census.gov/data/2019/acs/acs1/groups/{group}.json"
        )

    def test_stats_callsFetchInBatches(self):
        self.mocker.patch("census.api.fetch.MAX_QUERY_SIZE", 3)

        varCodes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        forDomain = GeoDomain("banana")
        inDomains = [GeoDomain("phone", "92")]

        for _ in self._service.stats(varCodes, forDomain, inDomains):
            pass

        assert self.requestsMock.get.call_args_list == [  # type: ignore
            call(
                "https://api.census.gov/data/2019/acs/acs1?get=NAME,1,2&for=banana:*&in=phone:92"
            ),
            call(
                "https://api.census.gov/data/2019/acs/acs1?get=NAME,3,4&for=banana:*&in=phone:92"
            ),
        ]

    def test_allVariables(self):
        self._service.allVariables()

        self.castMock(self.requestsMock.get).assert_called_once_with(  # type: ignore
            "https://api.census.gov/data/2019/acs/acs1/variables.json"
        )

    def test_stats_yieldsBatches(self):
        self.mocker.patch("census.api.fetch.MAX_QUERY_SIZE", 3)

        varCodes = [
            VariableCode("1"),
            VariableCode("2"),
            VariableCode("3"),
            VariableCode("4"),
        ]
        self.requestsMock.get.side_effect = [  # type: ignore
            MockRes(200, [["header1", "header2"], ["a", "b"], ["c", "d"]]),
            MockRes(200, [["header1", "header2"], ["e", "f"], ["g", "h"]]),
        ]

        res = self._service.stats(varCodes, GeoDomain(""), [GeoDomain("")])

        assert next(res) == [["header1", "header2"], ["a", "b"], ["c", "d"]]
        assert next(res) == [["header1", "header2"], ["e", "f"], ["g", "h"]]

        with pytest.raises(StopIteration):
            next(res)

    def test_healthCheck_pass(self, logMock: MagicMock):
        self.mocker.patch.object(self.requestsMock, "get", return_value=MockRes(200))

        self._service.healthCheck()

        self.castMock(logMock.debug).assert_called_once_with(  # type: ignore
            "[ApiFetchService] - healthCheck OK"
        )

    def test_healthCheck_fail(self, logMock: MagicMock):
        self.mocker.patch.object(self.requestsMock, "get", return_value=MockRes(404))

        msg = "Data does not exist for dataset=acs; survey=acs1; year=2019"

        with pytest.raises(CensusDoesNotExistException, match=msg):
            self._service.healthCheck()

        self.castMock(logMock.error).assert_called_once_with(  # type: ignore
            f"[ApiFetchService] - {msg}"
        )
        self.castMock(logMock.debug).assert_not_called()  # type: ignore
