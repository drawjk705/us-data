from typing import Dict, Generic, Tuple, Type, TypeVar
from unittest.mock import MagicMock
from abc import abstractmethod


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

    @abstractmethod
    def _getDependencies(self) -> Tuple[MagicMock, ...]:
        pass


@pytest.mark.usefixtures("apiFixture")
class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requestsMock: MagicMock
