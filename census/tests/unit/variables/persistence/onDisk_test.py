import pathlib
from unittest.mock import Mock

import pytest
from census.config import Config
from census.variables.persistence.onDisk import OnDiskCache
from pytest_mock.plugin import MockerFixture
from tests.serviceTestFixtures import ServiceTestFixture


@pytest.fixture
def config() -> Config:
    return Config(cacheDir="cache", shouldCacheOnDisk=True)


@pytest.fixture
def pathMock(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(pathlib.Path, "mkdir")


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("census.variables.persistence.onDisk.shutil.rmtree")


class DummyClass:
    pass


# we're using a dummy class here, since we're specifically
# testing the cache's constructor
class TestOnDiskCache(ServiceTestFixture[DummyClass]):
    @pytest.mark.parametrize("pathExists", [(True), (False)])
    def test_cacheInit(
        self,
        pathMock: Mock,
        shutilMock: Mock,
        config: Config,
        pathExists: bool,
    ):
        self.mocker.patch.object(pathlib.Path, "exists", lambda _: pathExists)  # type: ignore

        _ = OnDiskCache(config)

        if pathExists:
            shutilMock.assert_called_once_with("cache")
        else:
            shutilMock.assert_not_called()

        pathMock.assert_called_once_with(parents=True, exist_ok=True)
