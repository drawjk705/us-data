from typing import Dict, Generic, Tuple, Type, TypeVar
from unittest.mock import MagicMock
from abc import abstractmethod


from attr import dataclass
from pytest_mock.plugin import MockerFixture

_T = TypeVar("_T")


class ServiceTestFixture(Generic[_T]):
    _service: _T
    _dependencies: Dict[str, MagicMock]
    serviceType: Type[_T]
    mocker: MockerFixture

    @abstractmethod
    def _getDependencies(self) -> Tuple[MagicMock, ...]:
        pass


class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requestsMock: MagicMock


@dataclass
class FixtureNames:
    serviceFixture = "serviceFixture"
    injectMockerToClass = "injectMockerToClass"
    apiFixture = "apiFixture"
