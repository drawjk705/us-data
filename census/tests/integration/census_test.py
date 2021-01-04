import pathlib
from census.client.census import Census
from census.getCensus import getCensus
from census.exceptions import CensusDoesNotExistException
from typing import Any
from tests.integration.mockApiResponses import MOCK_API
import requests
from _pytest.monkeypatch import MonkeyPatch
import pytest
import os
import shutil


class _Response:
    status_code: int
    content: Any

    def __init__(self, status_code: int, content: Any) -> None:
        self.content = content
        self.status_code = status_code

    def json(self) -> Any:
        if self.status_code != 200:
            raise Exception("Uh oh")

        return self.content


@pytest.fixture(scope="function", autouse=True)
def mockRequests(monkeypatch: MonkeyPatch):
    def mockGet(route: str):
        res = MOCK_API.get(route)
        status_code = 404 if res is None else 200
        return _Response(status_code, res)

    monkeypatch.setattr(requests, "get", mockGet)


@pytest.fixture(scope="function", autouse=True)
def setPathToTest():
    parentPath = pathlib.Path(__file__).parent.absolute()

    os.chdir(parentPath)

    tempDir = pathlib.Path("temp")
    tempDir.mkdir(parents=True, exist_ok=False)

    os.chdir(tempDir.absolute())

    yield

    shutil.rmtree(tempDir.absolute())


@pytest.fixture
def census() -> Census:
    return getCensus(2019)


@pytest.mark.integration
class TestIntegration:
    def test_census_givenInvalidDataRequest(self):
        with pytest.raises(CensusDoesNotExistException, match=""):
            _ = getCensus(2020)

    def test_census_geography(self, census: Census):
        supportedGeos = census.getSupportedGeographies()
