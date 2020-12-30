from typing import Any, Dict
from collections import OrderedDict
import hypothesis.strategies as st
import pytest
from census.api.models import GeographyClauseSet, GeographyItem, GroupVariable
import census.api.parsing as parser
from hypothesis import assume
from hypothesis.core import given


@given(
    group=st.text(),
    concept=st.text(),
    varCode1=st.text(),
    label1=st.text(),
    predicateType1=st.text(),
    limit1=st.integers(),
    predicateOnly1=st.booleans(),
    varCode2=st.text(),
    label2=st.text(),
    predicateType2=st.text(),
    limit2=st.integers(),
    predicateOnly2=st.booleans(),
)
def test_parseVariableData(
    concept: str,
    group: str,
    varCode1: str,
    label1: str,
    predicateType1: str,
    limit1: int,
    predicateOnly1: bool,
    varCode2: str,
    label2: str,
    predicateType2: str,
    limit2: int,
    predicateOnly2: bool,
):
    assume(varCode1 != varCode2)

    variables = {
        "variables": {
            varCode1: {
                "label": label1,
                "concept": concept,
                "predicateType": predicateType1,
                "group": group,
                "limit": limit1,
                "predicateOnly": predicateOnly1,
            },
            varCode2: {
                "label": label2,
                "concept": concept,
                "predicateType": predicateType2,
                "group": group,
                "limit": limit2,
                "predicateOnly": predicateOnly2,
            },
        }
    }

    expectedVar1 = GroupVariable(varCode1, variables["variables"][varCode1])

    expectedVar2 = GroupVariable(varCode2, variables["variables"][varCode2])

    expected = [expectedVar1, expectedVar2]

    actual = parser.parseVariableData(variables)

    assert actual == expected


__supportedGeosTestCases = [
    (
        {
            "name": "principal city (or part)",
            "geoLevelDisplay": "312",
            "referenceDate": "2019-01-01",
            "requires": [
                "metropolitan statistical area/micropolitan statistical area",
                "state (or part)",
            ],
        },
        GeographyItem(
            name="principal city (or part)",
            hierarchy="312",
            clauses=(
                GeographyClauseSet(
                    forClause="principal city (or part):CODE",
                    inClauses=tuple(
                        [
                            "metropolitan statistical area/micropolitan statistical area:CODE",
                            "state (or part):CODE",
                        ]
                    ),
                ),
                GeographyClauseSet(
                    forClause="principal city (or part):*",
                    inClauses=tuple(
                        [
                            "metropolitan statistical area/micropolitan statistical area:CODE",
                            "state (or part):CODE",
                        ]
                    ),
                ),
            ),
        ),
    )
]


@pytest.mark.parametrize(["apiItem", "expectedParsedValue"], __supportedGeosTestCases)
def test_parseSupportedGeographies(
    apiItem: Dict[Any, Any], expectedParsedValue: GeographyItem
):
    apiResponse = {"default": [{"isDefault": True}], "fips": [apiItem]}

    res = parser.parseSupportedGeographies(apiResponse)

    assert res[apiItem["name"]] == expectedParsedValue
