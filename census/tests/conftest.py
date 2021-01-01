import inspect
from typing import Any, Dict, cast
from unittest.mock import MagicMock

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_mock.plugin import MockerFixture

# pyright: reportPrivateUsage=false


@pytest.fixture(scope="function")
def apiFixture(request: FixtureRequest, mocker: MockerFixture):
    request.cls.requestsMock = mocker.patch("census.api.fetch.requests")  # type: ignore


@pytest.fixture(scope="function")
def injectMockerToClass(request: FixtureRequest, mocker: MockerFixture):
    request.cls.mocker = mocker  # type: ignore


class _RequestCls:
    class Obj:
        serviceType: Any
        _service: Any
        _dependencies: Any

    cls: Obj


@pytest.fixture(scope="function")
def serviceFixture(request: FixtureRequest):
    req = cast(_RequestCls, request)
    obj = req.cls

    if obj.serviceType is None:
        raise Exception("Class must specify a serviceType attribute")

    dependencies: Dict[str, MagicMock] = {}

    for depName, depType in inspect.signature(obj.serviceType).parameters.items():
        if hasattr(depType.annotation, "__origin__"):
            dependencies.update({depName: MagicMock(depType.annotation.__origin__)})
        else:
            dependencies.update({depName: MagicMock(depType.annotation)})

    obj._service = obj.serviceType(**dependencies)
    obj._dependencies = dependencies
