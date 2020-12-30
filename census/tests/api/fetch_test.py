from typing import List
from unittest.mock import Mock

import census.api.fetch as fetch
import pytest
from census.api.ApiConfig import ApiConfig
from census.models import DatasetType, GeoDomain, SurveyType
from pytest_mock import MockerFixture


@pytest.fixture
def config() -> ApiConfig:
    apiConfig = ApiConfig(2020, DatasetType.ACS, SurveyType.ACS1)

    return apiConfig


@pytest.fixture
def fetchMock(mocker: MockerFixture) -> Mock:
    mocker.patch("census.api.fetch.__fetchData_Base")

    return fetch.__fetchData_Base  # type: ignore


@pytest.mark.parametrize(
    "domain,parentDomains,expectedRoute", [GeoDomain("us"), GeoDomain("state")]
)
def test_geographyCodes(
    config: ApiConfig,
    fetchMock: Mock,
    domain: GeoDomain,
    parentDomains: List[GeoDomain],
    expectedRoute: str,
):
    fetch.geographyCodes(config, domain)

    fetchMock.assert_called_once_with(config)
