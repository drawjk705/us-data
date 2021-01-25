import os
import re
import shutil
from pathlib import Path
from typing import Any, Callable, Collection, Dict, Generator, List, Optional, Set, cast

import pandas
import pytest
import requests
from _pytest.capture import CaptureFixture
from pytest_mock import MockerFixture

from tests.integration.census.mock_api_responses import MOCK_API
from tests.utils import MockRes
from the_census import Census, GeoDomain
from the_census._exceptions import CensusDoesNotExistException, NoCensusApiKeyException
from the_census._helpers import GeoDomainTypes
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


def verify_resource(
    resource: str,
    exists: bool = True,
    expected_data: Optional[List[Dict[str, Any]]] = None,
):
    path = Path(f"cache/2019/acs/acs1/{resource}")

    if not exists:
        assert not path.exists()
    else:
        assert path.exists()

        if expected_data:
            df = pandas.read_csv(path)  # type: ignore
            assert df.to_dict("records") == expected_data


@pytest.fixture(scope="function", autouse=True)
def api_calls(mocker: MockerFixture) -> Set[str]:
    _api_calls: Set[str] = set()

    def mockGet(route: str):
        route_without_api_key = re.sub(r"(\?|&)key=.*", "", route)

        _api_calls.add(route_without_api_key)

        res = cast(Collection[Any], MOCK_API.get(route_without_api_key))

        status_code = 404 if res is None else 200

        return MockRes(status_code, res)

    mocker.patch.object(requests, "get", mockGet)

    return _api_calls


@pytest.fixture(scope="function", autouse=True)
def set_current_path() -> Generator[None, None, None]:
    parent_path = Path(__file__).parent.absolute()

    os.chdir(parent_path)

    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=False)

    os.chdir(temp_dir.absolute())

    try:
        yield

    finally:
        os.chdir(parent_path)
        shutil.rmtree(temp_dir.absolute())


@pytest.fixture
def given_cache_with_group() -> None:
    Path("cache/2019/acs/acs1/").mkdir(parents=True, exist_ok=True)
    pandas.DataFrame(
        [
            dict(code="abc", description="alphabet", cleaned_name="Alphabet"),
            dict(code="123", description="numbers", cleaned_name="Numbers"),
        ]
    ).to_csv("./cache/2019/acs/acs1/groups.csv")
    verify_resource("groups.csv")


@pytest.fixture
def given_cache_with_variables() -> None:
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
    verify_resource("variables/varsForGroup.csv")


@pytest.fixture(autouse=True)
def given_env_var(mocker: MockerFixture):
    mocker.patch.object(os, "getenv", return_value="banana")


@pytest.mark.integration
class TestCensus:
    def test_invalid_data_request(self):
        with pytest.raises(
            CensusDoesNotExistException,
            match="Data does not exist for dataset=acs; survey=acs1; year=2020",
        ):
            _ = Census(2020)

    def test_no_environment_variable_set(self, mocker: MockerFixture):
        mocker.patch.object(os, "getenv", return_value=None)
        with pytest.raises(
            NoCensusApiKeyException, match="Could not find `CENSUS_API_KEY` in .env"
        ):
            _ = Census(2019)

    def test_no_caching_on_or_loading_from_disk(
        self,
    ):
        """This should not create a cache directory"""

        _ = Census(
            2019, should_load_from_existing_cache=False, should_cache_on_disk=False
        )

        assert not Path("cache").exists()

    def test_do_not_load_from_existing_cache(self, given_cache_with_group: None):
        """This should purge the existing cache"""

        assert len(list(Path("cache/2019/acs/acs1").iterdir())) > 0

        _ = Census(
            2019, should_load_from_existing_cache=False, should_cache_on_disk=True
        )

        assert Path("cache").exists()
        assert len(list(Path("cache/2019/acs/acs1").iterdir())) == 0

    def test_census_with_caching_and_loading_from_cache(
        self, api_calls: Set[str], given_cache_with_group: None
    ):
        census = Census(
            2019, should_load_from_existing_cache=True, should_cache_on_disk=True
        )

        census.get_groups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" not in api_calls

        assert Path("cache").exists()

    @pytest.mark.parametrize(
        "for_domain,in_domain",
        [
            (("congressional district",), ("state", "01")),
            (GeoDomain("congressional district"), GeoDomain("state", "01")),
        ],
    )
    def test_get_geography_codes(
        self, for_domain: GeoDomainTypes, in_domain: GeoDomainTypes
    ):
        census = Census(2019)

        codes = census.get_geography_codes(
            for_domain,
            in_domain,
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

    def test_groups_and_variables(self):
        # at first, there should be no groups in the on-disk cache
        census = Census(2019, should_cache_on_disk=True)
        verify_resource("groups.csv", exists=False)

        _ = census.get_groups()

        # once the API has been hit, the groups should now
        # be in the on-disk & in-memory caches
        group_codes = list(census.groups.values())
        verify_resource("groups.csv")
        assert len(group_codes) == 3

        # no variables should exist yet
        for code in group_codes:
            verify_resource(f"variables/{code}.csv", exists=False)

        variables = census.get_variables_by_group(*group_codes)

        # once the variables are retrieved,
        # verify that they exist in the on-disk cache...
        variables["cleaned_name"] = variables["name"].apply(clean_variable_name)
        for code in group_codes:
            verify_resource(
                f"variables/{code}.csv",
                exists=True,
                expected_data=[
                    variable
                    for variable in variables.to_dict("records")
                    if variable["group_code"] == code
                ],
            )
        # ...and in the in-memory cache
        assert len(census.variables) == 12

    def test_get_all_variables(self):
        census = Census(2019, should_cache_on_disk=True)

        allVars = census.get_all_variables()

        assert len(allVars.to_dict("records")) == 12
        assert len(census.variables) == 12

        for group, variables in allVars.groupby(["group_code"]):  # type: ignore
            variables["cleaned_name"] = variables["name"].apply(clean_variable_name)
            verify_resource(
                f"variables/{group}.csv",
                exists=True,
                expected_data=variables.to_dict("records"),
            )

    def test_groups_in_memory_cache_items(self):
        """This is a more in-depth test of the in-memory caching for groups"""

        census = Census(2019)

        _ = census.get_groups()

        assert dict(census.groups.items()) == {
            "PovertyStatusInThePast12MonthsOfFamiliesByFamilyTypeBySocialSecurityIncomeBySupplementalSecurityIncomeSsiAndCashPublicAssistanceIncome": "B17015",
            "SexByAgeByAmbulatoryDifficulty": "B18105",
            "SexByAgeByCognitiveDifficulty": "B18104",
        }

    def test_variables_in_memory_cache_items(self):
        """This is a more in-depth test of the in-memory caching for variables"""

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

    def test_supported_geographies_in_memory_and_on_disk_cache_items(self):
        census = Census(2019, should_cache_on_disk=True)

        verify_resource("supported_geographies.csv", exists=False)

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
        verify_resource("supported_geographies.csv")

    def test_search_groups(self):
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

    def test_search_variables_within_groups(self, api_calls: Set[str]):
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
        }.issubset(api_calls)
        assert res.to_dict("records") == expectedRes

    def test_search_all_variables(self, api_calls: Set[str]):
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
        }.issubset(api_calls)

        assert res.to_dict("records") == expectedRes

    @pytest.mark.parametrize("should_rename_columns", [(True), (False)])
    def test_stats_batches_api_calls(
        self, api_calls: Set[str], mocker: MockerFixture, should_rename_columns: bool
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
        }.issubset(api_calls)

    def test_stats_with_duplicate_variable_names_across_groups(self):
        """Some group variables can have the same name (e.g. EstimateTotal). This
        test verifies that in this case, variable names are suffixed with their group code
        """

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

    def test_stats_without_duplicate_variable_names_across_groups(self):
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
    def test_populate_repository(
        self,
        shouldLoadFromCache: bool,
        given_cache_with_group: None,
        given_cache_with_variables: None,
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
    def test_empty_api_responses(
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

    def test_help(self, capsys: CaptureFixture[str]):
        Census.help()

        out, _ = capsys.readouterr()

        assert (
            str(out)
            == "For more documentation on the census, see https://www2.census.gov/programs-surveys/\nFor more documentation on ACS subject defintiions, see https://www2.census.gov/programs-surveys/acs/tech_docs/subject_definitions/2019_ACSSubjectDefinitions.pdf\n"
        )

    def test_repr(self):
        c = Census(2019)

        assert str(c) == "<Census year=2019 dataset=acs survey=acs1>"
