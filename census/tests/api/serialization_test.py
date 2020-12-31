from census.api.serialization import ApiSerializationService
from typing import Any, Dict, Union
import hypothesis.strategies as st
import pytest
from census.api.models import GeographyClauseSet, GeographyItem, Group, GroupVariable
from hypothesis import assume
from hypothesis.core import given


@pytest.fixture
def service() -> ApiSerializationService:
    return ApiSerializationService()


@given(
    varCode1=st.text(),
    varCode2=st.text(),
    var1=st.fixed_dictionaries(
        {
            "label": st.text(),
            "concept": st.text(),
            "predicateType": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicateOnly": st.booleans(),
        }
    ),
    var2=st.fixed_dictionaries(
        {
            "label": st.text(),
            "concept": st.text(),
            "predicateType": st.text(),
            "group": st.text(),
            "limit": st.integers(),
            "predicateOnly": st.booleans(),
        }
    ),
)
def test_parseVariableData(
    varCode1: str,
    varCode2: str,
    var1: Dict[str, Union[str, int, bool]],
    var2: Dict[str, Union[str, int, bool]],
):
    assume(varCode1 != varCode2)

    service = ApiSerializationService()
    variables = {"variables": {varCode1: var1, varCode2: var2}}
    expectedVar1 = GroupVariable.fromJson(varCode1, var1)
    expectedVar2 = GroupVariable.fromJson(varCode2, var2)
    expected = [expectedVar1, expectedVar2]

    actual = service.parseVariableData(variables)

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
                    forClause="congressional district:CODE",
                    inClauses=["state:CODE"],
                ),
                GeographyClauseSet.makeSet(
                    forClause="congressional district:*", inClauses=[]
                ),
                GeographyClauseSet.makeSet(
                    forClause="congressional district:*",
                    inClauses=["state:*"],
                ),
            ],
        ),
    ),
]


@pytest.mark.parametrize(["apiItem", "expected"], __supportedGeosTestCases)
def test_parseSupportedGeographies(
    service: ApiSerializationService, apiItem: Dict[Any, Any], expected: GeographyItem
):
    apiResponse = {"default": [{"isDefault": True}], "fips": [apiItem]}

    res = service.parseSupportedGeographies(apiResponse)

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
def test_parseGroups(
    service: ApiSerializationService,
    groupResponse: Dict[Any, Any],
    expected: Dict[str, Group],
):
    actual = service.parseGroups(groupResponse)

    assert actual == expected
