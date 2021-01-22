from typing import Any, cast
from unittest.mock import MagicMock, Mock

import pandas
import pytest
from callee import String
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from the_census._config import Config
from the_census._persistence.onDisk import OnDiskCache


def make_cache(config: Config) -> OnDiskCache:
    return OnDiskCache(config, MagicMock())


@pytest.fixture
def path_mock(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("the_census._persistence.onDisk.Path")
    mocker.patch.object(mock(), "joinpath", return_value=mock())

    return mock


@pytest.fixture
def shutil_mock(mocker: MockerFixture) -> Mock:
    return mocker.patch("the_census._persistence.onDisk.shutil")


class DummyClass:
    ...


# we're using a dummy class here, since we're specifically
# testing the cache's constructor
class TestOnDiskCache(ServiceTestFixture[DummyClass]):
    @pytest.mark.parametrize(*shuffled_cases(pathExists=[True, False]))
    def test_cacheInit(
        self,
        path_mock: Mock,
        shutil_mock: Mock,
        pathExists: bool,
    ):
        config = Config(cache_dir="cache", should_cache_on_disk=True)
        self.given_existence_of_path(path_mock, pathExists)

        _ = make_cache(config)

        if pathExists:
            shutil_mock.rmtree.assert_called_once_with("cache")  # type: ignore
        else:
            shutil_mock.rmtree.assert_not_called()  # type: ignore

        path_mock().mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_cacheInit_givenArg_doesNotCreateCache(
        self, path_mock: MagicMock, shutil_mock: MagicMock
    ):
        config = Config(2019, should_cache_on_disk=False)

        _ = make_cache(config)

        path_mock().mkdir.assert_not_called()
        self.cast_mock(cast(Any, shutil_mock).rmtree).assert_not_called()

    @pytest.mark.parametrize(
        *shuffled_cases(
            should_cache_on_disk=[True, False],
            resource_exists=[True, False],
            should_load_from_existing_cache=[True, False],
        )
    )
    def test_put_givenShouldCacheOptions(
        self,
        should_cache_on_disk: bool,
        resource_exists: bool,
        path_mock: MagicMock,
        should_load_from_existing_cache: bool,
        shutil_mock: MagicMock,
    ):
        config = Config(
            2019,
            should_cache_on_disk=should_cache_on_disk,
            should_load_from_existing_cache=should_load_from_existing_cache,
        )
        resource = "resource"
        data = MagicMock(spec=pandas.DataFrame)
        self.given_existence_of_path(path_mock, resource_exists)

        cache = OnDiskCache(config, MagicMock())

        putRes = cache.put(resource, data)

        if should_cache_on_disk and not resource_exists:
            self.cast_mock(cast(Any, data).to_csv).assert_called_once_with(
                String(), index=False
            )

        assert putRes != (resource_exists and should_cache_on_disk)

    @pytest.mark.parametrize(
        *shuffled_cases(
            should_cache_on_disk=[True, False],
            resource_exists=[True, False],
            should_load_from_existing_cache=[True, False],
        )
    )
    def test_get_givenOptions(
        self,
        should_cache_on_disk: bool,
        path_mock: MagicMock,
        resource_exists: bool,
        should_load_from_existing_cache: bool,
        shutil_mock: MagicMock,
    ):
        config = Config(
            2019,
            should_cache_on_disk=should_cache_on_disk,
            should_load_from_existing_cache=should_load_from_existing_cache,
        )
        resource = "resource"

        cache = make_cache(config)

        self.given_existence_of_path(path_mock, resource_exists)
        mock_read_csv = MagicMock()
        get_retval = MagicMock(spec=pandas.DataFrame)
        mock_read_csv.return_value = get_retval

        self.mocker.patch.object(pandas, "read_csv", mock_read_csv)

        res = cache.get(resource)

        if (
            not should_cache_on_disk
            or not resource_exists
            or not should_load_from_existing_cache
        ):
            assert res.empty
            mock_read_csv.assert_not_called()
        else:
            mock_read_csv.assert_called_once()
            assert res == get_retval

    def given_existence_of_path(self, path_mock: MagicMock, exists: bool):
        self.mocker.patch.object(path_mock(), "exists", return_value=exists)
