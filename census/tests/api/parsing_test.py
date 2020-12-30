from typing import Any, Dict
import hypothesis.strategies as st
import pytest
from census.api.models import GeographyClauseSet, GeographyItem, Group, GroupVariable
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
        GeographyItem.makeItem(
            name="principal city (or part)",
            hierarchy="312",
            clauses=[
                GeographyClauseSet.makeSet(
                    forClause="principal city (or part):CODE",
                    inClauses=[
                        "metropolitan statistical area/micropolitan statistical area:CODE",
                        "state (or part):CODE",
                    ],
                ),
                GeographyClauseSet.makeSet(
                    forClause="principal city (or part):*",
                    inClauses=[
                        "metropolitan statistical area/micropolitan statistical area:CODE",
                        "state (or part):CODE",
                    ],
                ),
            ],
        ),
    ),
    (
        {
            "name": "congressional district",
            "geoLevelDisplay": "500",
            "referenceDate": "2019-01-01",
            "requires": ["state"],
            "wildcard": ["state"],
            "optionalWithWCFor": "state",
        },
        GeographyItem.makeItem(
            name="congressional district",
            hierarchy="500",
            clauses=[
                GeographyClauseSet.makeSet(
                    forClause="congressional district:*", inClauses=[]
                ),
                GeographyClauseSet.makeSet(
                    forClause="congressional district:*",
                    inClauses=["state:*"],
                ),
                GeographyClauseSet.makeSet(
                    forClause="congressional district:CODE",
                    inClauses=["state:CODE"],
                ),
            ],
        ),
    ),
]


@pytest.mark.parametrize(["apiItem", "expected"], __supportedGeosTestCases)
def test_parseSupportedGeographies(apiItem: Dict[Any, Any], expected: GeographyItem):
    apiResponse = {"default": [{"isDefault": True}], "fips": [apiItem]}

    res = parser.parseSupportedGeographies(apiResponse)

    actual = res[apiItem["name"]]

    assert actual == expected


@pytest.mark.parametrize(
    ["groupResponse", "expected"],
    [
        (
            {
                "groups": [
                    {
                        "name": "B17015",
                        "description": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                        "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B17015.json",
                    },
                    {
                        "name": "B18104",
                        "description": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                        "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
                    },
                ]
            },
            {
                "B17015": Group(
                    name="B17015",
                    description="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                    variables="https://api.census.gov/data/2019/acs/acs1/groups/B17015.json",
                ),
                "B18104": Group(
                    name="B18104",
                    description="SEX BY AGE BY COGNITIVE DIFFICULTY",
                    variables="https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
                ),
            },
        ),
    ],
)
def test_parseGroups(groupResponse: Dict[Any, Any], expected: Dict[str, Group]):
    actual = parser.parseGroups(groupResponse)

    assert actual == expected
