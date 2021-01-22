import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Collection, Dict, Generator, List, Optional, Set, cast

import pandas
import pytest
import requests
from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from tests.integration.census.mockApiResponses import MOCK_API
from tests.utils import MockRes
from the_census import Census, GeoDomain
from the_census._exceptions import CensusDoesNotExistException, NoCensusApiKeyException
from the_census._utils.clean_variable_name import clean_variable_name
from the_census._variables.models import Group, GroupCode, GroupVariable, VariableCode
from the_census._variables.repository.models import GroupSet, VariableSet

# pyright: reportUnknownMemberType=false


expectedStatsResWithoutNames = [
    {
        "B17015_001E": 172441.0,
        "B18104_001E": 664816.0,
        "B18105_001E": 664816.0,
        "NAME": "Congressional District 1 (116th Congress), Alabama",
        "congressional district": "01",
        "state": "01",
    },
    {
        "B17015_001E": 168129.0,
        "B18104_001E": 610312.0,
        "B18105_001E": 610312.0,
        "NAME": "Congressional District 2 (116th Congress), Alabama",
        "congressional district": "02",
        "state": "01",
    },
    {
        "B17015_001E": 184320.0,
        "B18104_001E": 664930.0,
        "B18105_001E": 664930.0,
        "NAME": "Congressional District 3 (116th Congress), Alabama",
        "congressional district": "03",
        "state": "01",
    },
    {
        "B17015_001E": 179508.0,
        "B18104_001E": 640347.0,
        "B18105_001E": 640347.0,
        "NAME": "Congressional District 4 (116th Congress), Alabama",
        "congressional district": "04",
        "state": "01",
    },
    {
        "B17015_001E": 195668.0,
        "B18104_001E": 681411.0,
        "B18105_001E": 681411.0,
        "NAME": "Congressional District 5 (116th Congress), Alabama",
        "congressional district": "05",
        "state": "01",
    },
    {
        "B17015_001E": 186592.0,
        "B18104_001E": 653559.0,
        "B18105_001E": 653559.0,
        "NAME": "Congressional District 6 (116th Congress), Alabama",
        "congressional district": "06",
        "state": "01",
    },
    {
        "B17015_001E": 151225.0,
        "B18104_001E": 620542.0,
        "B18105_001E": 620542.0,
        "NAME": "Congressional District 7 (116th Congress), Alabama",
        "congressional district": "07",
        "state": "01",
    },
]

expectedStatsResWithNames = [
    {
        "Estimate_Total_B17015": 172441.0,
        "Estimate_Total_B18104": 664816.0,
        "Estimate_Total_B18105": 664816.0,
        "NAME": "Congressional District 1 (116th Congress), Alabama",
        "congressional district": "01",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 168129.0,
        "Estimate_Total_B18104": 610312.0,
        "Estimate_Total_B18105": 610312.0,
        "NAME": "Congressional District 2 (116th Congress), Alabama",
        "congressional district": "02",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 184320.0,
        "Estimate_Total_B18104": 664930.0,
        "Estimate_Total_B18105": 664930.0,
        "NAME": "Congressional District 3 (116th Congress), Alabama",
        "congressional district": "03",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 179508.0,
        "Estimate_Total_B18104": 640347.0,
        "Estimate_Total_B18105": 640347.0,
        "NAME": "Congressional District 4 (116th Congress), Alabama",
        "congressional district": "04",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 195668.0,
        "Estimate_Total_B18104": 681411.0,
        "Estimate_Total_B18105": 681411.0,
        "NAME": "Congressional District 5 (116th Congress), Alabama",
        "congressional district": "05",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 186592.0,
        "Estimate_Total_B18104": 653559.0,
        "Estimate_Total_B18105": 653559.0,
        "NAME": "Congressional District 6 (116th Congress), Alabama",
        "congressional district": "06",
        "state": "01",
    },
    {
        "Estimate_Total_B17015": 151225.0,
        "Estimate_Total_B18104": 620542.0,
        "Estimate_Total_B18105": 620542.0,
        "NAME": "Congressional District 7 (116th Congress), Alabama",
        "congressional district": "07",
        "state": "01",
    },
]


def verifyResource(
    resource: str,
    exists: bool = True,
    expectedData: Optional[List[Dict[str, Any]]] = None,
):
    path = Path(f"cache/2019/acs/acs1/{resource}")

    if not exists:
        assert not path.exists()
    else:
        assert path.exists()

        if expectedData:
            df = pandas.read_csv(path)  # type: ignore
            assert df.to_dict("records") == expectedData


@pytest.fixture(scope="function", autouse=True)
def apiCalls(monkeypatch: MonkeyPatch) -> Set[str]:
    _apiCalls: Set[str] = set()

    def mockGet(route: str):
        routeWithoutKey = re.sub(r"(\?|&)key=.*", "", route)
        _apiCalls.add(routeWithoutKey)
        res = cast(Collection[Any], MOCK_API.get(routeWithoutKey))
        status_code = 404 if res is None else 200
        return MockRes(status_code, res)

    monkeypatch.setattr(requests, "get", mockGet)

    return _apiCalls


@pytest.fixture(scope="function", autouse=True)
def setPathToTest() -> Generator[None, None, None]:
    parentPath = Path(__file__).parent.absolute()

    os.chdir(parentPath)

    tempDir = Path("temp")
    if tempDir.exists():
        shutil.rmtree(tempDir)

    tempDir.mkdir(parents=True, exist_ok=False)

    os.chdir(tempDir.absolute())

    try:
        yield
    finally:
        os.chdir(parentPath)
        shutil.rmtree(tempDir.absolute())


@pytest.fixture
def givenCacheWithGroup() -> None:
    Path("cache/2019/acs/acs1/").mkdir(parents=True, exist_ok=True)
    pandas.DataFrame(
        [
            dict(code="abc", description="alphabet", cleaned_name="Alphabet"),
            dict(code="123", description="numbers", cleaned_name="Numbers"),
        ]
    ).to_csv("./cache/2019/acs/acs1/groups.csv")
    verifyResource("groups.csv")


@pytest.fixture
def givenCacheWithVariables() -> None:
    Path("cache/2019/acs/acs1/variables/").mkdir(parents=True, exist_ok=True)
    pandas.DataFrame(
        [
            dict(
                code="v1",
                group_code="g1",
                group_concept="group 1",
                name="variable 1",
                predicate_type="int",
                predicate_only=True,
                limit=0,
                cleaned_name="Variable 1",
            ),
            dict(
                code="v2",
                group_code="g1",
                group_concept="group 1",
                name="variable 2",
                predicate_type="int",
                predicate_only=True,
                limit=0,
                cleaned_name="Variable 2",
            ),
        ]
    ).to_csv("./cache/2019/acs/acs1/variables/varsForGroup.csv")
    verifyResource("variables/varsForGroup.csv")


@pytest.fixture(autouse=True)
def givenEnvVar(mocker: MockerFixture):
    mocker.patch.object(os, "getenv", return_value="banana")


@pytest.mark.integration
class TestCensus:
    def test_census_givenInvalidDataRequest(self):
        with pytest.raises(
            CensusDoesNotExistException,
            match="Data does not exist for dataset=acs; survey=acs1; year=2020",
        ):
            _ = Census(2020)

    def test_census_givenNoEnvironmentVariable(self, mocker: MockerFixture):
        mocker.patch.object(os, "getenv", return_value=None)
        with pytest.raises(
            NoCensusApiKeyException, match="Could not find `CENSUS_API_KEY` in .env"
        ):
            _ = Census(2019)

    def test_census_givenNotCachingOnDiskAndNoLoadingFromDisk_doesNotCreateCache(
        self,
    ):
        _ = Census(
            2019, should_load_from_existing_cache=False, should_cache_on_disk=False
        )

        assert not Path("cache").exists()

    def test_census_givenCensusDoesNotLoadFromExistingCache_purgesExistingCache(
        self, givenCacheWithGroup: None
    ):
        _ = Census(
            2019, should_load_from_existing_cache=False, should_cache_on_disk=True
        )

        assert Path("cache").exists()
        assert len(list(Path("cache/2019/acs/acs1").iterdir())) == 0

    def test_census_createsCacheAndLoadsItOnQuery(
        self, apiCalls: Set[str], givenCacheWithGroup: None
    ):
        census = Census(
            2019, should_load_from_existing_cache=True, should_cache_on_disk=True
        )

        census.get_groups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" not in apiCalls
        assert len(apiCalls) == 1

        assert Path("cache").exists()

    def test_census_get_geography_codes(
        self,
    ):
        census = Census(2019)

        codes = census.get_geography_codes(
            GeoDomain("congressional district"),
            GeoDomain("state", "01"),
        )

        expected = [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "01",
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "02",
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "03",
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "04",
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "05",
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "06",
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "07",
            },
        ]

        assert codes.to_dict("records") == expected

    def test_census_groupsAndVariables(self):
        census = Census(2019, should_cache_on_disk=True)
        verifyResource("groups.csv", exists=False)

        _ = census.get_groups()

        GroupCodes = list(census.groups.values())
        verifyResource("groups.csv")
        assert len(GroupCodes) == 3

        for code in GroupCodes:
            verifyResource(f"variables/{code}.csv", exists=False)

        variables = census.get_variables_by_group(*GroupCodes)
        variables["cleaned_name"] = variables["name"].apply(clean_variable_name)
        for code in GroupCodes:
            verifyResource(
                f"variables/{code}.csv",
                exists=True,
                expectedData=[
                    variable
                    for variable in variables.to_dict("records")
                    if variable["group_code"] == code
                ],
            )

        assert len(census.variables) == 12

    def test_census_get_all_variables(self):
        census = Census(2019, should_cache_on_disk=True)
        allVars = census.get_all_variables()

        assert len(allVars.to_dict("records")) == 12
        assert len(census.variables) == 12

        for group, variables in allVars.groupby(["group_code"]):  # type: ignore
            variables["cleaned_name"] = variables["name"].apply(clean_variable_name)
            verifyResource(
                f"variables/{group}.csv",
                exists=True,
                expectedData=variables.to_dict("records"),
            )

    def test_census_groups_populatesGroupNames(self):
        census = Census(2019)

        _ = census.get_groups()

        assert dict(census.groups.items()) == {
            "PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome": "B17015",
            "SexByAgeByAmbulatoryDifficulty": "B18105",
            "SexByAgeByCognitiveDifficulty": "B18104",
        }

    def test_census_variables_populatesVariableNames(self):
        census = Census(2019)

        census.get_all_variables()

        assert dict(census.variables.items()) == {
            "AnnotationOfEstimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001EA"),
                group_code=GroupCode("B17015"),
                group_concept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfEstimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001EA"),
                group_code=GroupCode("B18104"),
                group_concept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfEstimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001EA"),
                group_code=GroupCode("B18105"),
                group_concept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfEstimate_Total",
            ),
            "AnnotationOfMarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001MA"),
                group_code=GroupCode("B17015"),
                group_concept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfMarginOfError_Total",
            ),
            "AnnotationOfMarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001MA"),
                group_code=GroupCode("B18104"),
                group_concept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfMarginOfError_Total",
            ),
            "AnnotationOfMarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001MA"),
                group_code=GroupCode("B18105"),
                group_concept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Annotation of Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="string",
                cleaned_name="AnnotationOfMarginOfError_Total",
            ),
            "Estimate_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001E"),
                group_code=GroupCode("B17015"),
                group_concept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="Estimate_Total",
            ),
            "Estimate_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001E"),
                group_code=GroupCode("B18104"),
                group_concept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="Estimate_Total",
            ),
            "Estimate_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001E"),
                group_code=GroupCode("B18105"),
                group_concept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Estimate!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="Estimate_Total",
            ),
            "MarginOfError_Total_B17015": GroupVariable(
                code=VariableCode("B17015_001M"),
                group_code=GroupCode("B17015"),
                group_concept="POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                name="Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="MarginOfError_Total",
            ),
            "MarginOfError_Total_B18104": GroupVariable(
                code=VariableCode("B18104_001M"),
                group_code=GroupCode("B18104"),
                group_concept="SEX BY AGE BY COGNITIVE DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="MarginOfError_Total",
            ),
            "MarginOfError_Total_B18105": GroupVariable(
                code=VariableCode("B18105_001M"),
                group_code=GroupCode("B18105"),
                group_concept="SEX BY AGE BY AMBULATORY DIFFICULTY",
                name="Margin of Error!!Total:",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="MarginOfError_Total",
            ),
        }

    def test_census_supported_geographies(self):
        census = Census(2019, should_cache_on_disk=True)

        verifyResource("supported_geographies.csv", exists=False)

        _ = census.get_supported_geographies()

        in_mem_supported_geos = census.supported_geographies

        assert in_mem_supported_geos.__dict__ == {
            "CongressionalDistrict": "congressional district",
            "County": "county",
            "Division": "division",
            "Region": "region",
            "State": "state",
            "Us": "us",
        }
        verifyResource("supported_geographies.csv")

    def test_census_search_groups(self):
        census = Census(2019)
        regex = r"sex by age by .* difficulty"

        res = census.search_groups(regex)

        expectedRes = [
            {
                "code": "B18104",
                "description": "SEX BY AGE BY COGNITIVE DIFFICULTY",
            },
            {
                "code": "B18105",
                "description": "SEX BY AGE BY AMBULATORY DIFFICULTY",
            },
        ]

        assert res.to_dict("records") == expectedRes

    def test_census_search_variables_within_groups(self, apiCalls: Set[str]):
        census = Census(2019)
        regex = r"estimate"

        res = census.search_variables(regex, GroupCode("B18104"), GroupCode("B18105"))

        expectedRes = [
            {
                "code": "B18104_001E",
                "group_code": "B18104",
                "group_concept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "int",
            },
            {
                "code": "B18104_001EA",
                "group_code": "B18104",
                "group_concept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "string",
            },
            {
                "code": "B18105_001E",
                "group_code": "B18105",
                "group_concept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "int",
            },
            {
                "code": "B18105_001EA",
                "group_code": "B18105",
                "group_concept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "string",
            },
        ]

        assert {
            "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json",
            "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json",
        }.issubset(apiCalls)
        assert res.to_dict("records") == expectedRes

    def test_census_searchall_variables(self, apiCalls: Set[str]):
        census = Census(2019)
        regex = r"estimate"

        res = census.search_variables(regex)

        expectedRes = [
            {
                "code": "B17015_001E",
                "group_code": "B17015",
                "group_concept": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY "
                "TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY "
                "INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "int",
            },
            {
                "code": "B17015_001EA",
                "group_code": "B17015",
                "group_concept": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY "
                "TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY "
                "INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "string",
            },
            {
                "code": "B18104_001E",
                "group_code": "B18104",
                "group_concept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "int",
            },
            {
                "code": "B18104_001EA",
                "group_code": "B18104",
                "group_concept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "string",
            },
            {
                "code": "B18105_001E",
                "group_code": "B18105",
                "group_concept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "int",
            },
            {
                "code": "B18105_001EA",
                "group_code": "B18105",
                "group_concept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicate_only": True,
                "predicate_type": "string",
            },
        ]

        assert {
            "https://api.census.gov/data/2019/acs/acs1/variables.json",
        }.issubset(apiCalls)

        assert res.to_dict("records") == expectedRes

    @pytest.mark.parametrize("should_rename_columns", [(True), (False)])
    def test_census_stats_batchedApiCalls(
        self, apiCalls: Set[str], mocker: MockerFixture, should_rename_columns: bool
    ):
        census = Census(2019, replace_column_headers=should_rename_columns)

        mocker.patch("the_census._api.fetch.MAX_QUERY_SIZE", 2)

        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        for_domain = GeoDomain("congressional district")
        in_domains = [GeoDomain("state", "01")]
        _ = census.get_all_variables()

        res = census.get_stats(variables, for_domain, *in_domains)

        assert res.to_dict("records") == (
            expectedStatsResWithNames
            if should_rename_columns
            else expectedStatsResWithoutNames
        )

        assert {
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B17015_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18104_001E&for=congressional%20district:*&in=state:01",
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B18105_001E&for=congressional%20district:*&in=state:01",
        }.issubset(apiCalls)

    def test_census_stats_columnNameChangeWithDuplicate(self):
        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        for_domain = GeoDomain("congressional district")
        in_domains = [GeoDomain("state", "01")]

        census = Census(
            2019,
            replace_column_headers=True,
        )

        # to populate "variables"
        _ = census.get_all_variables()

        res = census.get_stats(variables, for_domain, *in_domains)

        assert res.to_dict("records") == [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "congressional district": "01",
                "state": "01",
                "Estimate_Total_B17015": 172441,
                "Estimate_Total_B18104": 664816,
                "Estimate_Total_B18105": 664816,
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "congressional district": "02",
                "state": "01",
                "Estimate_Total_B17015": 168129,
                "Estimate_Total_B18104": 610312,
                "Estimate_Total_B18105": 610312,
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total_B17015": 184320,
                "Estimate_Total_B18104": 664930,
                "Estimate_Total_B18105": 664930,
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total_B17015": 179508,
                "Estimate_Total_B18104": 640347,
                "Estimate_Total_B18105": 640347,
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "congressional district": "05",
                "state": "01",
                "Estimate_Total_B17015": 195668,
                "Estimate_Total_B18104": 681411,
                "Estimate_Total_B18105": 681411,
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total_B17015": 186592,
                "Estimate_Total_B18104": 653559,
                "Estimate_Total_B18105": 653559,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total_B17015": 151225,
                "Estimate_Total_B18104": 620542,
                "Estimate_Total_B18105": 620542,
            },
        ]

    def test_census_stats_columnNameChangeWithoutDuplicate(self):
        variables = [VariableCode("B17015_001E")]
        for_domain = GeoDomain("congressional district")
        in_domains = [GeoDomain("state", "01")]

        census = Census(
            2019,
            should_load_from_existing_cache=True,
            should_cache_on_disk=True,
            replace_column_headers=True,
        )

        # to populate "variables"
        _ = census.get_all_variables()

        res = census.get_stats(variables, for_domain, *in_domains)

        assert res.to_dict("records") == [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "congressional district": "01",
                "state": "01",
                "Estimate_Total": 172441,
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "congressional district": "02",
                "state": "01",
                "Estimate_Total": 168129,
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "congressional district": "03",
                "state": "01",
                "Estimate_Total": 184320,
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "congressional district": "04",
                "state": "01",
                "Estimate_Total": 179508,
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "congressional district": "05",
                "state": "01",
                "Estimate_Total": 195668,
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "congressional district": "06",
                "state": "01",
                "Estimate_Total": 186592,
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "congressional district": "07",
                "state": "01",
                "Estimate_Total": 151225,
            },
        ]

    @pytest.mark.parametrize("shouldLoadFromCache", [(True), (False)])
    def test_census_givenLoadFromCache_populatesRepository(
        self,
        shouldLoadFromCache: bool,
        givenCacheWithGroup: None,
        givenCacheWithVariables: None,
    ):

        census = Census(
            2019,
            should_load_from_existing_cache=shouldLoadFromCache,
            should_cache_on_disk=True,
        )
        expectedRepoVars = VariableSet(
            GroupVariable(
                code=VariableCode("v1"),
                group_code=GroupCode("g1"),
                group_concept="group 1",
                name="variable 1",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="Variable 1",
            ),
            GroupVariable(
                code=VariableCode("v2"),
                group_code=GroupCode("g1"),
                group_concept="group 1",
                name="variable 2",
                limit=0,
                predicate_only=True,
                predicate_type="int",
                cleaned_name="Variable 2",
            ),
        )
        expectedRepoGroups = GroupSet(
            Group(GroupCode("abc"), "alphabet", cleaned_name="Alphabet"),
            Group(GroupCode("123"), "numbers", cleaned_name="Numbers"),
        )

        repoVars = census.variables
        repoGroups = census.groups

        if shouldLoadFromCache:
            assert repoVars == expectedRepoVars
            assert repoGroups == expectedRepoGroups
        else:
            assert len(repoVars) == 0
            assert len(repoGroups) == 0

    @pytest.mark.parametrize(
        "censusCall",
        [
            lambda census: cast(Census, census).get_supported_geographies(),  # type: ignore
            lambda census: cast(Census, census).get_geography_codes(GeoDomain("somewhere")),  # type: ignore
            lambda census: cast(Census, census).get_all_variables(),  # type: ignore
            lambda census: cast(Census, census).get_groups(),  # type: ignore
            lambda census: cast(Census, census).get_variables_by_group(),  # type: ignore
            lambda census: cast(Census, census).search_groups(GroupCode("g-123")),  # type: ignore
            lambda census: cast(Census, census).search_variables("regex"),  # type: ignore
        ],
    )
    def test_emptyResponses(
        self, censusCall: Callable[[Census], pandas.DataFrame], mocker: MockerFixture
    ):
        mocker.patch.object(requests, "get", return_value=MockRes(204))

        census = Census(2019)

        assert censusCall(census).empty

    def test_list_available_datasets(self):
        datasets = Census.list_available_datasets()

        assert datasets.to_dict("records") == [
            {
                "dataset": "ecneoyinv",
                "description": "This dataset presents statistics for Wholesale Trade:  "
                "Inventories by Valuation Method for the U.S.",
                "name": "Economic Census: Economic Census of the United States: Wholesale "
                "Trade: Inventories by Valuation Method for the U.S.",
                "survey": "",
                "year": 2017,
            },
            {
                "dataset": "dec",
                "description": "Summary File 4 is repeated or iterated for the total "
                "population and 335 additional population groups: 132 race "
                "groups,78 American Indian and Alaska Native tribe categories, "
                "39 Hispanic or Latino groups, and 86 ancestry groups.Tables "
                "for any population group excluded from SF 2 because the "
                "group's total population in a specific geographic area did "
                "not meet the SF 2 threshold of 100 people are excluded from "
                "SF 4. Tables in SF 4 shown for any of the above population "
                "groups will only be shown if there are at least 50 unweighted "
                "sample cases in a specific geographic area. The same 50 "
                "unweighted sample cases also applied to ancestry iterations. "
                "In an iterated file such as SF 4, the universes households, "
                "families, and occupied housing units are classified by the "
                "race or ethnic group of the householder. The universe "
                "subfamilies is classified by the race or ethnic group of the "
                "reference person for the subfamily. In a husband/wife "
                "subfamily, the reference person is the husband; in a "
                "parent/child subfamily, the reference person is always the "
                "parent. The universes population in households, population in "
                "families, and population in subfamilies are classified by the "
                "race or ethnic group of the inidviduals within the household, "
                "family, or subfamily without regard to the race or ethnicity "
                "of the householder. Notes follow selected tables to make the "
                "classification of the universe clear. In any population table "
                "where there is no note, the universe classification is always "
                "based on the race or ethnicity of the person. In all housing "
                "tables, the universe classification is based on the race or "
                "ethnicity of the householder.",
                "name": "Decennial Census: Summary File 4",
                "survey": "sf4",
                "year": 2000,
            },
        ]

    def test_repr(self):
        c = Census(2019)

        assert str(c) == "<Census year=2019 dataset=acs survey=acs1>"
