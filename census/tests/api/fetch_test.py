from typing import List
from census.config import Config
from census.api.interface import IApiSerializationService

import pytest
from census.api.fetch import ApiFetchService
from census.models import DatasetType, GeoDomain, SurveyType
from tests.base import ApiServiceTestFixture, FixtureNames

mockConfig = Config(year=2019, datasetType=DatasetType.ACS, surveyType=SurveyType.ACS1)


class ApiServiceWrapper(ApiFetchService):
    def __init__(self, parser: IApiSerializationService) -> None:
        super().__init__(config=mockConfig, parser=parser)


@pytest.mark.usefixtures(FixtureNames.apiFixture, FixtureNames.serviceFixture)
class TestApiFetchService(ApiServiceTestFixture[ApiServiceWrapper]):
    serviceType = ApiServiceWrapper

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

    def test_variable_callsFetch(self):
        group = "abc123"

        self._service.variablesForGroup(group)

        self.requestsMock.get.assert_called_with(  # type: ignore
            f"https://api.census.gov/data/2019/acs/acs1/groups/{group}.json"
        )
