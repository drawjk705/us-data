import pathlib
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from census.config import Config
from census.dataCache.onDisk import OnDiskCache
from pytest_mock.plugin import MockerFixture
from tests.base import FixtureNames, ServiceTestFixture


@pytest.fixture
def config() -> MagicMock:
    return MagicMock(Config)


@pytest.fixture
def pathMock(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(pathlib.Path, "mkdir")


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("census.dataCache.onDisk.shutil.rmtree")


@pytest.mark.usefixtures(FixtureNames.injectMockerToClass)
class TestOnDiskCache(ServiceTestFixture[Any]):
    @pytest.mark.parametrize("pathExists", [(True), (False)])
    def test_cacheInit(
        self,
        pathMock: Mock,
        shutilMock: Mock,
        config: MagicMock,
        pathExists: bool,
    ):
        self.mocker.patch.object(pathlib.Path, "exists", lambda _: pathExists)  # type: ignore

        _ = OnDiskCache(config)

        if pathExists:
            shutilMock.assert_called_once_with("cache")
        else:
            shutilMock.assert_not_called()

        pathMock.assert_called_once_with(parents=True, exist_ok=True)
