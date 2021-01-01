import inspect
from typing import Any, Dict, cast
from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch
from _pytest.fixtures import FixtureRequest
from pytest_mock.plugin import MockerFixture

# pyright: reportPrivateUsage=false


@pytest.fixture(autouse=True)
def no_requests(monkeypatch: MonkeyPatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


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

    # this lets us see all of the service's constructor types
    for depName, depType in inspect.signature(obj.serviceType).parameters.items():
        # this condition will be true if the service inherits
        # from a generic class
        if hasattr(depType.annotation, "__origin__"):
            dependencies.update({depName: MagicMock(depType.annotation.__origin__)})
        else:
            dependencies.update({depName: MagicMock(depType.annotation)})

    # we call the service's constructor with the mocked dependencies
    # and set the test class obj's _service attribute to hold this service
    obj._service = obj.serviceType(**dependencies)
    # and we do the same with the test class obj's _dependencies attribute
    obj._dependencies = dependencies
