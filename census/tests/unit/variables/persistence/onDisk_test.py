import itertools
import pathlib
from typing import Any, List, Tuple
from callee import String  # type: ignore
from unittest.mock import MagicMock, Mock
from _pytest.monkeypatch import MonkeyPatch
from hypothesis.core import given
import pandas
from hypothesis import given
import hypothesis.strategies as st

import pytest
from census.config import Config
from census.variables.persistence.onDisk import OnDiskCache
from pytest_mock.plugin import MockerFixture
from tests.serviceTestFixtures import ServiceTestFixture


def makeBoolPermutations(n: int) -> List[Tuple[bool, ...]]:
    return list(itertools.product([True, False], repeat=n))


@pytest.fixture
def pathMock(monkeypatch: MonkeyPatch) -> Mock:
    pathMock = MagicMock(spec=pathlib.Path)

    def getPathMock(*args: Any, **kwargs: Any):
        mockPath = pathMock()
        mockPath.joinpath.return_value = mockPath
        return pathMock()

    monkeypatch.setattr(pathlib, "Path", getPathMock)
    return pathMock


def givenExistenceOfPath(pathExists: bool, mocker: MockerFixture) -> None:
    mocker.patch.object(pathlib.Path, "exists", return_value=pathExists)


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("census.variables.persistence.onDisk.shutil")


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
        pathExists: bool,
        monkeypatch: MonkeyPatch,
    ):
        config = Config(cacheDir="cache", shouldCacheOnDisk=True)
        pathMock().exists.return_value = pathExists

        _ = OnDiskCache(config)

        if pathExists:
            shutilMock.rmtree.assert_called_once_with("cache")  # type: ignore
        else:
            shutilMock.rmtree.assert_not_called()  # type: ignore

        pathMock().mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_cacheInit_givenArg_doesNotCreateCache(
        self, pathMock: Mock, shutilMock: Mock
    ):
        config = Config(2019, shouldCacheOnDisk=False)

        _ = OnDiskCache(config)

        pathMock().mkdir.assert_not_called()  # type: ignore
        self.castMock(shutilMock.rmtree).assert_not_called()  # type: ignore

    @given(shouldCacheOnDisk=st.booleans(), resourceExists=st.booleans())
    def test_put_givenShouldCacheOptions(
        self,
        shouldCacheOnDisk: bool,
        resourceExists: bool,
    ):
        config = Config(2019, shouldCacheOnDisk=shouldCacheOnDisk)
        resource = "resource"
        data = MagicMock(spec=pandas.DataFrame)
        givenExistenceOfPath(resourceExists, self.mocker)

        cache = OnDiskCache(config)

        putRes = cache.put(resource, data)

        if shouldCacheOnDisk and not resourceExists:
            self.castMock(data.to_csv).assert_called_once_with(String(), index=False)  # type: ignore

        assert putRes == (shouldCacheOnDisk and not resourceExists)

    @pytest.mark.parametrize(
        ["shouldCacheOnDisk", "resourceExists", "shouldLoadFromExistingCache"],
        makeBoolPermutations(3),
    )
    def test_get_givenOptions(
        self,
        shouldCacheOnDisk: bool,
        resourceExists: bool,
        shouldLoadFromExistingCache: bool,
        monkeypatch: MonkeyPatch,
    ):
        config = Config(
            2019,
            shouldCacheOnDisk=shouldCacheOnDisk,
            shouldLoadFromExistingCache=shouldLoadFromExistingCache,
        )
        resource = "resource"
        cache = OnDiskCache(config)
        mockFn = MagicMock()
        mockFn.return_value = "banana"
        monkeypatch.setattr(
            pathlib.Path, "exists", lambda *args, **kwargs: resourceExists
        )
        monkeypatch.setattr(pandas, "read_csv", mockFn)

        res = cache.get(resource)

        if (
            not shouldCacheOnDisk
            or not resourceExists
            or not shouldLoadFromExistingCache
        ):
            assert res.empty
            mockFn.assert_not_called()
        else:
            mockFn.assert_called_once()
            assert res == "banana"
