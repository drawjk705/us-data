from census.variables.models import GroupCode, VariableCode
import pandas
from census.models import GeoDomain
from pathlib import Path
from census.client.census import Census
from census.getCensus import getCensus
from census.exceptions import CensusDoesNotExistException
from typing import Any, Set
from tests.integration.mockApiResponses import MOCK_API
import requests
from _pytest.monkeypatch import MonkeyPatch
import pytest
import os
import shutil


class _Response:
    status_code: int
    content: Any

    def __init__(self, status_code: int, content: Any) -> None:
        self.content = content
        self.status_code = status_code

    def json(self) -> Any:
        if self.status_code != 200:
            raise Exception("Uh oh")

        return self.content


def verifyResource(resource: str, exists: bool = True):
    if not exists:
        assert not Path(f"cache/2019/acs/acs1/{resource}").exists()
    else:
        assert Path(f"cache/2019/acs/acs1/{resource}").exists()


@pytest.fixture(scope="function", autouse=True)
def apiCalls(monkeypatch: MonkeyPatch):
    _apiCalls: Set[str] = set()

    def mockGet(route: str):
        _apiCalls.add(route)
        res = MOCK_API.get(route)
        status_code = 404 if res is None else 200
        return _Response(status_code, res)

    monkeypatch.setattr(requests, "get", mockGet)

    return _apiCalls


@pytest.fixture(scope="function", autouse=True)
def setPathToTest():
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
def tempDir() -> Path:
    return Path()


@pytest.fixture
def censusNoCache() -> Census:
    return getCensus(2019, shouldCacheOnDisk=False)


@pytest.fixture
def censusCacheNoLoad() -> Census:
    return getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=False)


@pytest.fixture
def cachedCensus() -> Census:
    return getCensus(2019, shouldCacheOnDisk=True, shouldLoadFromExistingCache=True)


@pytest.mark.integration
class TestCensus:
    def test_census_givenInvalidDataRequest(self):
        with pytest.raises(CensusDoesNotExistException, match=""):
            _ = getCensus(2020)

    def test_censusNoCache_doesNotCreateCache(
        self, censusNoCache: Census, tempDir: Path
    ):
        _ = censusNoCache.getGroups()

        assert not tempDir.joinpath("cache").exists()

    def test_censusCacheNoLoad_createsCacheButDoesNotLoadIt(
        self, censusCacheNoLoad: Census, tempDir: Path, apiCalls: Set[str]
    ):
        tempDir.joinpath("cache").mkdir(parents=True, exist_ok=True)
        pandas.DataFrame(
            [
                dict(code="abc", description="alphabet"),
                dict(code="123", description="numbers"),
            ]
        ).to_csv("./cache/2019/acs/acs1/groups.csv")
        verifyResource("groups.csv")

        _ = censusCacheNoLoad.getGroups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" in apiCalls

        assert tempDir.joinpath("cache").exists()

    def test_cachedCensus_createsCacheAndLoadsItOnQuery(
        self, cachedCensus: Census, tempDir: Path, apiCalls: Set[str]
    ):
        tempDir.joinpath("cache").mkdir(parents=True, exist_ok=True)
        pandas.DataFrame(
            [
                dict(code="abc", description="alphabet"),
                dict(code="123", description="numbers"),
            ]
        ).to_csv("./cache/2019/acs/acs1/groups.csv")
        verifyResource("groups.csv")

        _ = cachedCensus.getGroups()

        assert "https://api.census.gov/data/2019/acs/acs1/groups.json" not in apiCalls
        assert len(apiCalls) == 1

        assert tempDir.joinpath("cache").exists()

    def test_cachedCensus_getGeographyCodes(self, cachedCensus: Census, tempDir: Path):
        codes = cachedCensus.getGeographyCodes(
            forDomain=GeoDomain("congressional district"),
            inDomains=[GeoDomain("state", "01")],
        )

        expected = [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "01",
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "03",
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "05",
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "04",
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "07",
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "02",
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "06",
            },
        ]

        assert codes.to_dict("records") == expected

    def test_cachedCensus_groupsAndVariables(self, cachedCensus: Census):
        verifyResource("groups.csv", exists=False)
        _ = cachedCensus.getGroups()
        groupCodes = [groupCode for groupCode in cachedCensus.groups.keys()]
        verifyResource("groups.csv")
        assert len(groupCodes) == 3

        for code in groupCodes:
            verifyResource(f"variables/{code}.csv", exists=False)
        _ = cachedCensus.getVariablesByGroup(groupCodes)
        for code in groupCodes:
            verifyResource(f"variables/{code}.csv")

        assert len(cachedCensus.variables) == 12

    def test_cachedCensus_getAllVariables(self, cachedCensus: Census):
        allVars = cachedCensus.getAllVariables()

        assert len(allVars.to_dict("records")) == 12
        assert len(cachedCensus.variables) == 12

        for group, _ in allVars.groupby(["groupCode"]):  # type: ignore
            verifyResource(f"variables/{group}.csv")

    def test_cachedCensus_supportedGeographies(self, cachedCensus: Census):
        verifyResource("supportedGeographies.csv", exists=False)

        _ = cachedCensus.getSupportedGeographies()

        verifyResource("supportedGeographies.csv")

    def test_cachedCensus_searchGroups(self, cachedCensus: Census):
        regex = r"sex by age by .* difficulty"

        res = cachedCensus.searchGroups(regex)

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

    def test_cachedCensus_searchVariablesWithinGroups(
        self, cachedCensus: Census, apiCalls: Set[str]
    ):
        regex = r"estimate"

        res = cachedCensus.searchVariables(
            regex, "name", inGroups=[GroupCode("B18104"), GroupCode("B18105")]
        )

        expectedRes = [
            {
                "code": "B18104_001E",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18104_001EA",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "B18105_001E",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18105_001EA",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
        ]

        assert (
            "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json" in apiCalls
            and "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json"
            in apiCalls
        )
        assert res.to_dict("records") == expectedRes

    def test_cachedCensus_searchAllVariables(
        self, cachedCensus: Census, apiCalls: Set[str]
    ):
        regex = r"estimate"

        res = cachedCensus.searchVariables(
            regex, "name", inGroups=[GroupCode("B18104"), GroupCode("B18105")]
        )

        expectedRes = [
            {
                "code": "B18104_001E",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18104_001EA",
                "groupCode": "B18104",
                "groupConcept": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
            {
                "code": "B18105_001E",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "int",
            },
            {
                "code": "B18105_001EA",
                "groupCode": "B18105",
                "groupConcept": "SEX BY AGE BY AMBULATORY DIFFICULTY",
                "limit": 0,
                "name": "Annotation of Estimate!!Total:",
                "predicateOnly": True,
                "predicateType": "string",
            },
        ]

        assert (
            "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json" in apiCalls
            and "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json"
            in apiCalls
            and "https://api.census.gov/data/2019/acs/acs1/groups/B18105.json"
            in apiCalls
        )
        assert res.to_dict("records") == expectedRes

    def test_cachedCensus_stats(self, cachedCensus: Census, apiCalls: Set[str]):
        variables = [
            VariableCode(code)
            for code in "B17015_001E,B18104_001E,B18105_001E".split(",")
        ]
        forDomain = GeoDomain("congressional district")
        inDomains = [GeoDomain("state", "01")]

        res = cachedCensus.getStats(variables, forDomain, inDomains)

        expectedRes = [
            {
                "NAME": "Congressional District 1 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "01",
                "B17015_001E": "172441",
                "B18104_001E": "664816",
                "B18105_001E": "664816",
            },
            {
                "NAME": "Congressional District 3 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "03",
                "B17015_001E": "184320",
                "B18104_001E": "664930",
                "B18105_001E": "664930",
            },
            {
                "NAME": "Congressional District 5 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "05",
                "B17015_001E": "195668",
                "B18104_001E": "681411",
                "B18105_001E": "681411",
            },
            {
                "NAME": "Congressional District 4 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "04",
                "B17015_001E": "179508",
                "B18104_001E": "640347",
                "B18105_001E": "640347",
            },
            {
                "NAME": "Congressional District 7 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "07",
                "B17015_001E": "151225",
                "B18104_001E": "620542",
                "B18105_001E": "620542",
            },
            {
                "NAME": "Congressional District 2 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "02",
                "B17015_001E": "168129",
                "B18104_001E": "610312",
                "B18105_001E": "610312",
            },
            {
                "NAME": "Congressional District 6 (116th Congress), Alabama",
                "state": "01",
                "congressional district": "06",
                "B17015_001E": "186592",
                "B18104_001E": "653559",
                "B18105_001E": "653559",
            },
        ]

        print(res.to_dict("records"))

        assert res.to_dict("records") == expectedRes
        assert (
            "https://api.census.gov/data/2019/acs/acs1?get=NAME,B17015_001E,B18104_001E,B18105_001E&for=congressional%20district:*&in=state:01"
            in apiCalls
        )
