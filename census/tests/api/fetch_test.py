from typing import List
from unittest.mock import Mock, patch

from hypothesis.core import given

import census.api.fetch as fetch
import hypothesis.strategies as st
import pytest
from census.api.ApiConfig import ApiConfig
from census.models import DatasetType, GeoDomain, SurveyType
from pytest_mock import MockerFixture


@pytest.fixture(scope="module")
def apiConfig() -> ApiConfig:
    config = ApiConfig(2020, DatasetType.ACS, SurveyType.ACS1)

    return config


@pytest.fixture()
def fetchMock(mocker: MockerFixture) -> Mock:
    mocker.patch("census.api.fetch.__fetchData_Base")

    return fetch.__fetchData_Base  # type: ignore


@pytest.mark.parametrize(
    ["domain", "parentDomains", "expectedRoute"],
    [
        (GeoDomain("state"), [GeoDomain("us")], "?get=NAME&for=state:*&in=us:*"),
        (
            GeoDomain("county", "01"),
            [GeoDomain("state", "01")],
            "?get=NAME&for=county:01&in=state:01",
        ),
        (
            GeoDomain("county", "01"),
            [GeoDomain("state", "01"), GeoDomain("us")],
            "?get=NAME&for=county:01&in=state:01&in=us:*",
        ),
    ],
)
def test_geographyCodes(
    apiConfig: ApiConfig,
    fetchMock: Mock,
    domain: GeoDomain,
    parentDomains: List[GeoDomain],
    expectedRoute: str,
):
    fetch.geographyCodes(apiConfig, domain, parentDomains)

    fetchMock.assert_called_once_with(apiConfig, route=expectedRoute)


def test_groupData_callsFetch(apiConfig: ApiConfig, fetchMock: Mock):
    fetch.groupData(apiConfig)

    fetchMock.assert_called_once_with(apiConfig, route="/groups.json")


def test_supportedGeographies_callsFetch(
    apiConfig: ApiConfig, fetchMock: Mock, mocker: MockerFixture
):
    mocker.patch("census.api.parsing.parseSupportedGeographies")
    fetch.supportedGeographies(apiConfig)

    fetchMock.assert_called_once_with(apiConfig, route="/geography.json")


@given(group=st.text())
def test_variableData_callsFetch(apiConfig: ApiConfig, group: str):
    with patch("census.api.fetch.__fetchData_Base") as fetchMock:
        fetch.variableData(group, apiConfig)

        fetchMock.assert_called_with(apiConfig, route=f"/groups/{group}.json")
