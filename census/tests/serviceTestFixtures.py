from typing import Any, Dict, Generic, Type, TypeVar, cast
from unittest.mock import MagicMock


from pytest_mock.plugin import MockerFixture
import pytest

# pyright: reportPrivateUsage=false

_T = TypeVar("_T")


@pytest.mark.usefixtures("injectMockerToClass", "serviceFixture")
class ServiceTestFixture(Generic[_T]):
    _service: _T
    _dependencies: Dict[str, MagicMock]
    serviceType: Type[_T]
    mocker: MockerFixture

    def mockDep(self, dependency: Any) -> MagicMock:
        return cast(MagicMock, dependency)


@pytest.mark.usefixtures("apiFixture")
class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requestsMock: MagicMock
