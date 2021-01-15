import pytest

from us_data.census._utils.cleanVariableName import cleanVariableName


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
