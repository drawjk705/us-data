from census.config import Config
from census.api.fetch import ApiFetchService
from census.api.serialization import ApiSerializationService
from typing import List
from unittest.mock import MagicMock, Mock, patch

import hypothesis.strategies as st
import pytest
from census.models import DatasetType, GeoDomain, SurveyType
from hypothesis.core import given
from pytest_mock import MockerFixture


@pytest.fixture(scope="module")
def service() -> ApiFetchService:
    config = Config(2019, DatasetType.ACS, SurveyType.ACS1)
    serializer = MagicMock(ApiSerializationService)
    fetchService = ApiFetchService(config, serializer)

    return fetchService


@pytest.fixture()
def fetchMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("census.api.fetch.requests.get")


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
    service: ApiFetchService,
    fetchMock: Mock,
    domain: GeoDomain,
    parentDomains: List[GeoDomain],
    expectedRoute: str,
):
    service.geographyCodes(domain, parentDomains)

    fetchMock.assert_called_once_with(expectedRoute)


def test_groupData_callsFetch(service: ApiFetchService, fetchMock: Mock):
    service.groupData()

    fetchMock.assert_called_once_with(
        "https://api.census.gov/data/2019/acs/acs1/groups.json"
    )


def test_supportedGeographies_callsFetch(
    service: ApiFetchService, fetchMock: Mock, mocker: MockerFixture
):
    service.supportedGeographies()

    fetchMock.assert_called_once_with(
        "https://api.census.gov/data/2019/acs/acs1/geography.json"
    )


@given(group=st.text())
def test_variable_callsFetch(service: ApiFetchService, group: str):
    with patch("census.api.fetch.requests.get") as fetchMock:
        service.variables(group)

        fetchMock.assert_called_with(
            f"https://api.census.gov/data/2019/acs/acs1/groups/{group}.json"
        )
