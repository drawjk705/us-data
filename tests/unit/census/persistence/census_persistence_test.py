from unittest.mock import MagicMock, Mock

import pandas
import pytest
from callee import String
from pytest import MonkeyPatch
from pytest_mock.plugin import MockerFixture

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import shuffledCases
from us_data.census._config import Config
from us_data.census._persistence.onDisk import OnDiskCache


def makeCache(config: Config) -> OnDiskCache:
    return OnDiskCache(config, MagicMock())


@pytest.fixture
def pathMock(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("us_data.census._persistence.onDisk.Path")
    mocker.patch.object(mock(), "joinpath", return_value=mock())

    return mock


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("us_data.census._persistence.onDisk.shutil")


class DummyClass:
    ...


# we're using a dummy class here, since we're specifically
# testing the cache's constructor
class TestOnDiskCache(ServiceTestFixture[DummyClass]):
    @pytest.mark.parametrize(*shuffledCases(pathExists=[True, False]))
    def test_cacheInit(
        self,
        pathMock: Mock,
        shutilMock: Mock,
        pathExists: bool,
    ):
        config = Config(cacheDir="cache", shouldCacheOnDisk=True)
        self.givenExistenceOfPath(pathMock, pathExists)

        _ = makeCache(config)

        if pathExists:
            shutilMock.rmtree.assert_called_once_with("cache")  # type: ignore
        else:
            shutilMock.rmtree.assert_not_called()  # type: ignore

        pathMock().mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_cacheInit_givenArg_doesNotCreateCache(
        self, pathMock: MagicMock, shutilMock: Mock
    ):
        config = Config(2019, shouldCacheOnDisk=False)

        _ = makeCache(config)

        pathMock().mkdir.assert_not_called()  # type: ignore
        self.castMock(shutilMock.rmtree).assert_not_called()  # type: ignore

    @pytest.mark.parametrize(
        *shuffledCases(
            shouldCacheOnDisk=[True, False],
            resourceExists=[True, False],
            shouldLoadFromExistingCache=[True, False],
        )
    )
    def test_put_givenShouldCacheOptions(
        self,
        shouldCacheOnDisk: bool,
        resourceExists: bool,
        pathMock: MagicMock,
        shouldLoadFromExistingCache: bool,
        shutilMock: MagicMock,
    ):
        config = Config(
            2019,
            shouldCacheOnDisk=shouldCacheOnDisk,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache,
        )
        resource = "resource"
        data = MagicMock(spec=pandas.DataFrame)
        self.givenExistenceOfPath(pathMock, resourceExists)

        cache = OnDiskCache(config, MagicMock())

        putRes = cache.put(resource, data)

        if shouldCacheOnDisk and not resourceExists:
            self.castMock(data.to_csv).assert_called_once_with(String(), index=False)  # type: ignore

        assert putRes != (resourceExists and shouldCacheOnDisk)

    @pytest.mark.parametrize(
        *shuffledCases(
            shouldCacheOnDisk=[True, False],
            resourceExists=[True, False],
            shouldLoadFromExistingCache=[True, False],
        )
    )
    def test_get_givenOptions(
        self,
        shouldCacheOnDisk: bool,
        pathMock: MagicMock,
        resourceExists: bool,
        shouldLoadFromExistingCache: bool,
        monkeypatch: MonkeyPatch,
        shutilMock: MagicMock,
    ):
        config = Config(
            2019,
            shouldCacheOnDisk=shouldCacheOnDisk,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache,
        )
        resource = "resource"

        cache = makeCache(config)

        self.givenExistenceOfPath(pathMock, resourceExists)
        mockReadCsv = MagicMock()
        getRetval = MagicMock(spec=pandas.DataFrame)
        mockReadCsv.return_value = getRetval
        monkeypatch.setattr(pandas, "read_csv", mockReadCsv)

        res = cache.get(resource)

        if (
            not shouldCacheOnDisk
            or not resourceExists
            or not shouldLoadFromExistingCache
        ):
            assert res.empty
            mockReadCsv.assert_not_called()
        else:
            mockReadCsv.assert_called_once()
            assert res == getRetval

    def givenExistenceOfPath(self, pathMock: MagicMock, exists: bool):
        self.mocker.patch.object(pathMock(), "exists", return_value=exists)
