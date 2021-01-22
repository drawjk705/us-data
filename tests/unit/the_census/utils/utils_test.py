import pytest

from the_census._utils.clean_variable_name import clean_variable_name


@pytest.mark.parametrize(
    ["variableName", "cleaned_name"],
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
def test_clean_variable_name(variableName: str, cleaned_name: str):
    res = clean_variable_name(variableName)

    assert res == cleaned_name
