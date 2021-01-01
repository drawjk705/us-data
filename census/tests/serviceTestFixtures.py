import inspect
from typing import Any, Dict, Generic, Tuple, Type, TypeVar, cast
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

    def setUpService(self) -> None:
        if self.serviceType is None:
            raise Exception("Class must specify a serviceType attribute")

        dependencies: Dict[str, MagicMock] = {}

        # this lets us see all of the service's constructor types
        for depName, depType in inspect.signature(self.serviceType).parameters.items():
            # this condition will be true if the service inherits
            # from a generic class
            if hasattr(depType.annotation, "__origin__"):
                dependencies.update({depName: MagicMock(depType.annotation.__origin__)})
            else:
                dependencies.update({depName: MagicMock(depType.annotation)})

        # we call the service's constructor with the mocked dependencies
        # and set the test class obj's _service attribute to hold this service
        self._service = cast(Any, self.serviceType)(**dependencies)
        # and we do the same with the test class obj's _dependencies attribute
        self._dependencies = dependencies


@pytest.mark.usefixtures("apiFixture")
class ApiServiceTestFixture(ServiceTestFixture[_T]):
    requestsMock: MagicMock
