import logging
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from census.utils.chunk import chunk
from census.utils.cleanVariableName import cleanVariableName
from census.utils.timer import timer
from census.utils.unique import getUnique


def test_chunk_givenChunkLessThanSize():
    items = [1, 2, 3, 4]
    n = 2

    for i, subset in enumerate(chunk(items, n)):
        if i == 0:
            assert subset == [1, 2]
        elif i == 1:
            assert subset == [3, 4]


def test_chunk_givenChunkGreaterThanSize():
    items = [1, 2, 3, 4]
    n = 5

    for i, subset in enumerate(chunk(items, n)):
        assert i == 0
        assert subset == items


def test_getUnique_preservesOrder():
    items = [1, 2, 3, 4, 5, 1]

    res = getUnique(items)

    assert res == [1, 2, 3, 4, 5]


def test_timer_logsAndReturnsValues(mocker: MockerFixture):
    @timer
    def fn() -> int:
        return 1

    mockLogging = mocker.patch("census.utils.timer.logging")
    mockLogger = MagicMock()
    cast(MagicMock, cast(logging, mockLogging).getLogger).return_value = mockLogger
    mockPerfCounter = mocker.patch("census.utils.timer.time")
    mockPerfCounter.perf_counter.side_effect = [1, 2]  # type: ignore

    retval = fn()

    cast(MagicMock, mockLogger.debug).assert_called_once_with(  # type: ignore
        "[test_timer_logsAndReturnsValues.<locals>.fn] - duration: 1000.00ms"
    )
    assert retval == 1


@pytest.mark.parametrize(
    ["variableName", "cleanedName"],
    [
        ("Estimate!!Total:", "Estimate_Total"),
        ("banana", "Banana"),
        (
            "Estimate!!Total:!!No schooling completed",
            "Estimate_Total_NoSchoolingCompleted",
        ),
        (
            "Estimate!!Total:!!No schooling completed, nothing at all",
            "Estimate_Total_NoSchoolingCompletedNothingAtAll",
        ),
    ],
)
def test_cleanVariableName(variableName: str, cleanedName: str):
    res = cleanVariableName(variableName)

    assert res == cleanedName
