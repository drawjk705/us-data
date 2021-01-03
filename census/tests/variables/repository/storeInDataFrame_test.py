from census.variables.models import Group, GroupCode, GroupVariable, VariableCode
from census.models import GeoDomain
from typing import List, cast

from census.variables.repository.storeInDataFrame import VariableRepository

from _pytest.monkeypatch import MonkeyPatch
from tests.serviceTestFixtures import ServiceTestFixture
import pandas
import pytest
from unittest.mock import MagicMock

# pyright: reportPrivateUsage = false


apiRetval = "banana"


class TestVariableStorageService(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getGroups_givenCacheRetval(self, isCacheHit: bool):
        fullDf = pandas.DataFrame(
            [
                Group("1", "desc1").__dict__,
                Group("2", "desc2").__dict__,
            ]
        )

        self.mocker.patch.object(
            self._service._cache, "get", return_value=fullDf if isCacheHit else None
        )

        apiFetch = self.mocker.patch.object(
            self._service._api, "groupData", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "groups", return_value=fullDf
        )

        self._service.getGroups()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.mockDep(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.mockDep(self._service._cache.put).assert_called_once_with(
                "groups.csv", fullDf
            )

    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getSupportedGeographies(self, isCacheHit: bool):
        fullDf = pandas.DataFrame(
            [
                {"name": "us", "hierarchy": 1, "for": "this", "in": "that"},
                {"name": "them", "hierarchy": 2, "for": "that", "in": "this"},
            ]
        )

        self.mocker.patch.object(
            self._service._cache, "get", return_value=fullDf if isCacheHit else None
        )
        apiFetch = self.mocker.patch.object(
            self._service._api, "supportedGeographies", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "supportedGeographies", return_value=fullDf
        )

        self._service.getSupportedGeographies()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.mockDep(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.mockDep(self._service._cache.put).assert_called_once_with(
                "supportedGeographies.csv", fullDf
            )

    def test_getGeographyCodes(self):
        forDomain = MagicMock()
        inDomains = [MagicMock()]

        fullDf = pandas.DataFrame(
            [
                {
                    "name": "banana",
                    "state": "01",
                },
                {
                    "name": "apple",
                    "state": "01",
                },
            ]
        )

        apiFetch = self.mocker.patch.object(
            self._service._api, "geographyCodes", return_value=apiRetval
        )
        transform = self.mocker.patch.object(
            self._service._transformer, "geographyCodes", return_value=fullDf
        )

        res = self._service.getGeographyCodes(
            forDomain, cast(List[GeoDomain], inDomains)
        )

        apiFetch.assert_called_once_with(forDomain, inDomains)
        transform.assert_called_once_with(apiRetval)

        assert res.to_dict() == fullDf.to_dict()

    def test_getVariablesByGroup(self):
        cacheHitGroup = GroupCode("hit")
        cacheMissGroup = GroupCode("miss")

        variables = pandas.DataFrame(
            [
                GroupVariable(
                    code=VariableCode("1"),
                    groupCode=GroupCode("G1"),
                    groupConcept="fruit",
                    limit=0,
                    name="variable 1",
                    predicateOnly=False,
                    predicateType="int",
                ).__dict__,
                GroupVariable(
                    code=VariableCode("2"),
                    groupCode=GroupCode("G1"),
                    groupConcept="fruit",
                    limit=0,
                    name="variable 2",
                    predicateOnly=False,
                    predicateType="int",
                ).__dict__,
            ]
        )

        transformer = self.mockDep(self._service._transformer)
        cache = self.mockDep(self._service._cache)

        self.mocker.patch.object(transformer, "variables", return_value=variables)

        def cacheGetSideEffect(resource: str) -> pandas.DataFrame:
            return variables if cacheHitGroup in resource else pandas.DataFrame()

        self.mocker.patch.object(cache, "get", side_effect=cacheGetSideEffect)

        self._service.getVariablesByGroup([cacheHitGroup, cacheMissGroup])
