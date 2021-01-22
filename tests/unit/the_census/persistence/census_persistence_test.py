from unittest.mock import MagicMock, Mock

import pandas
import pytest
from callee import String
from pytest import MonkeyPatch
from pytest_mock.plugin import MockerFixture

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import shuffledCases
from the_census._config import Config
from the_census._persistence.onDisk import OnDiskCache


def makeCache(config: Config) -> OnDiskCache:
    return OnDiskCache(config, MagicMock())


@pytest.fixture
def pathMock(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("the_census._persistence.onDisk.Path")
    mocker.patch.object(mock(), "joinpath", return_value=mock())

    return mock


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("the_census._persistence.onDisk.shutil")


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
        config = Config(cache_dir="cache", should_cache_on_disk=True)
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
        config = Config(2019, should_cache_on_disk=False)

        _ = makeCache(config)

        pathMock().mkdir.assert_not_called()  # type: ignore
        self.castMock(shutilMock.rmtree).assert_not_called()  # type: ignore

    @pytest.mark.parametrize(
        *shuffledCases(
            should_cache_on_disk=[True, False],
            resourceExists=[True, False],
            should_load_from_existing_cache=[True, False],
        )
    )
    def test_put_givenShouldCacheOptions(
        self,
        should_cache_on_disk: bool,
        resourceExists: bool,
        pathMock: MagicMock,
        should_load_from_existing_cache: bool,
        shutilMock: MagicMock,
    ):
        config = Config(
            2019,
            should_cache_on_disk=should_cache_on_disk,
            should_load_from_existing_cache=should_load_from_existing_cache,
        )
        resource = "resource"
        data = MagicMock(spec=pandas.DataFrame)
        self.givenExistenceOfPath(pathMock, resourceExists)

        cache = OnDiskCache(config, MagicMock())

        putRes = cache.put(resource, data)

        if should_cache_on_disk and not resourceExists:
            self.castMock(data.to_csv).assert_called_once_with(String(), index=False)  # type: ignore

        assert putRes != (resourceExists and should_cache_on_disk)

    @pytest.mark.parametrize(
        *shuffledCases(
            should_cache_on_disk=[True, False],
            resourceExists=[True, False],
            should_load_from_existing_cache=[True, False],
        )
    )
    def test_get_givenOptions(
        self,
        should_cache_on_disk: bool,
        pathMock: MagicMock,
        resourceExists: bool,
        should_load_from_existing_cache: bool,
        monkeypatch: MonkeyPatch,
        shutilMock: MagicMock,
    ):
        config = Config(
            2019,
            should_cache_on_disk=should_cache_on_disk,
            should_load_from_existing_cache=should_load_from_existing_cache,
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
            not should_cache_on_disk
            or not resourceExists
            or not should_load_from_existing_cache
        ):
            assert res.empty
            mockReadCsv.assert_not_called()
        else:
            mockReadCsv.assert_called_once()
            assert res == getRetval

    def givenExistenceOfPath(self, pathMock: MagicMock, exists: bool):
        self.mocker.patch.object(pathMock(), "exists", return_value=exists)
