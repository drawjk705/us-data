from typing import Any


class ServiceTestFixtureException(Exception):
    pass


class _RequestCls:
    class Obj:
        serviceType: Any
        _service: Any
        _dependencies: Any

    cls: Obj


def extractService(obj: _RequestCls.Obj) -> Any:
    """
    This is some clever hackery to get the class type
    of the TypeVar that we pass in to `ServiceTestFixture`.
    So if we create a test suite such as:

    ```python3
    class Suite(ServiceTestFixture[MyService]):
        pass
    ```

    this function will get the class type of `MyService`,
    as opposed to just treating `MyService` like a generic
    type.

    Args:
        obj (_RequestCls.Obj): Instance of the test suite
        retrieved with pytest

    Raises:
        ServiceTestFixtureException

    Returns:
        The class type of the service in question
    """

    # this lets us get the class that our test fixture
    # is inheriting from (i.e., ServiceTestFixture[T])
    fixtureClass = [
        base
        for base in obj.__dict__["__orig_bases__"]
        if "ServiceTestFixture[" in str(base)
    ]
    if len(fixtureClass) != 1:
        raise ServiceTestFixtureException(
            "Test Suite is inheriting from more than one class"
        )

    fixtureClass = fixtureClass[0]

    # here, we try to extract the class type of the
    # type argument passed in (the `T`) in `ServiceTestFixture[T]`
    if not hasattr(fixtureClass, "__args__"):
        raise ServiceTestFixtureException(
            "ServiceTestFixture does not have any type arguments"
        )

    if len(fixtureClass.__args__) != 1:
        raise ServiceTestFixtureException("ServiceTestFixture needs one type argument")

    return fixtureClass.__args__[0]
