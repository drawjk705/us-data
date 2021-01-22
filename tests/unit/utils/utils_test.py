import time
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from the_census._utils.chunk import chunk
from the_census._utils.clean_variable_name import clean_variable_name
from the_census._utils.timer import timer
from the_census._utils.unique import get_unique


def test_chunk_with_chunk_size_less_than_list_length():
    items = [1, 2, 3, 4]
    n = 2

    for i, subset in enumerate(chunk(items, n)):
        if i == 0:
            assert subset == [1, 2]
        elif i == 1:
            assert subset == [3, 4]


def test_chunk_with_chunk_size_greater_than_list_length():
    items = [1, 2, 3, 4]
    n = 5

    for i, subset in enumerate(chunk(items, n)):
        assert i == 0
        assert subset == items


def test_get_unique_preserves_order():
    items = [1, 2, 3, 4, 5, 1]

    res = get_unique(items)

    assert res == [1, 2, 3, 4, 5]


def test_timer_logs_and_returns_values(mocker: MockerFixture):
    @timer
    def fn() -> int:
        return 1

    mock_logging = mocker.patch("the_census._utils.timer.logging")
    mock_logger = MagicMock()
    mocker.patch.object(mock_logging, "getLogger", return_value=mock_logger)
    mocker.patch.object(time, "perf_counter", side_effect=[1, 2])

    retval = fn()

    cast(MagicMock, cast(Any, mock_logger).debug).assert_called_once_with(
        "[test_timer_logs_and_returns_values.<locals>.fn] - duration: 1000.00ms"
    )
    assert retval == 1


@pytest.mark.parametrize(
    ["variable_name", "cleaned_name"],
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
def test_clean_variable_name(variable_name: str, cleaned_name: str):
    res = clean_variable_name(variable_name)

    assert res == cleaned_name
