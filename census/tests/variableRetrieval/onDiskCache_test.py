from census.config import Config
import pathlib
from unittest.mock import MagicMock, Mock

import pytest
from census.variableRetrieval.onDiskCache import OnDiskCache
from pytest_mock.plugin import MockerFixture


@pytest.fixture
def config() -> MagicMock:
    return MagicMock(Config)


@pytest.fixture
def pathMock(mocker: MockerFixture) -> Mock:
    return mocker.patch.object(pathlib.Path, "mkdir")


@pytest.fixture
def shutilMock(mocker: MockerFixture) -> Mock:
    return mocker.patch("census.variableRetrieval.onDiskCache.shutil.rmtree")


@pytest.mark.parametrize("pathExists", [(True), (False)])
def test_cacheInit(
    pathMock: Mock,
    shutilMock: Mock,
    config: MagicMock,
    pathExists: bool,
    mocker: MockerFixture,
):
    mocker.patch.object(pathlib.Path, "exists", lambda _: pathExists)  # type: ignore

    _ = OnDiskCache(config)

    if pathExists:
        shutilMock.assert_called_once_with("cache")
    else:
        shutilMock.assert_not_called()

    pathMock.assert_called_once_with(parents=True, exist_ok=True)
