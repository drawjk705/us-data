from typing import Any, Dict, Generic, TypeVar, cast
from unittest.mock import MagicMock
from _pytest.monkeypatch import MonkeyPatch


from pytest_mock.plugin import MockerFixture
import pytest

# pyright: reportPrivateUsage=false

_T = TypeVar("_T")


@pytest.mark.usefixtures(
    "injectMockerToClass", "serviceFixture", "injectMonkeyPatchToClass"
)
class ServiceTestFixture(Generic[_T]):
    _service: _T
    _dependencies: Dict[str, MagicMock]
    mocker: MockerFixture
    monkeypatch: MonkeyPatch

    def castMock(self, dependency: Any) -> MagicMock:
        return cast(MagicMock, dependency)


@pytest.mark.usefixtures("apiFixture")
class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requestsMock: MagicMock
