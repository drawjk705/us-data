from census.variables.models import TGroupCode
from census.models import GeoDomain
from typing import List, cast

from census.variables.repository.storeInDataFrame import VariableRepository

from _pytest.monkeypatch import MonkeyPatch
from tests.serviceTestFixtures import ServiceTestFixture
import pandas
import pytest
from unittest.mock import MagicMock

# pyright: reportPrivateUsage = false


emptyDf = pandas.DataFrame()
fullDf = pandas.DataFrame({"col": [1, 2, 3]})

apiRetval = "banana"
transformerRetval = "apple"


class TestVariableStorageService(ServiceTestFixture[VariableRepository]):
    serviceType = VariableRepository

    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getGroups_givenCacheRetval(
        self,
        isCacheHit: bool,
        monkeypatch: MonkeyPatch,
    ):
        monkeypatch.setattr(pandas, "DataFrame", lambda: emptyDf)

        popCodes = self.mocker.patch.object(self._service, "_populateCodes")

        api = self.mockDep(self._service._api)
        transformer = self.mockDep(self._service._transformer)
        cache = self.mockDep(self._service._cache)

        self.mocker.patch.object(
            cache, "get", return_value=fullDf if isCacheHit else None
        )

        cachePut = self.mocker.patch.object(cache, "put")
        transGroups = self.mocker.patch.object(
            transformer, "groups", return_value=transformerRetval
        )
        apiGroup = self.mocker.patch.object(api, "groupData", return_value=apiRetval)

        self._service.getGroups()

        if isCacheHit:
            apiGroup.assert_not_called()
            transGroups.assert_not_called()
            cachePut.assert_not_called()
            popCodes.assert_called_once_with(
                fullDf, self._service.groupCodes, TGroupCode, "description"
            )
        else:
            apiGroup.assert_called_once()
            transGroups.assert_called_once_with(apiRetval)
            cachePut.assert_called_once_with("groups.csv", transformerRetval)
            popCodes.assert_called_once_with(
                transformerRetval, self._service.groupCodes, TGroupCode, "description"
            )

    @pytest.mark.parametrize("isCacheHit", (True, False))
    def test_getSupportedGeographies(self, isCacheHit: bool):
        api = self.mockDep(self._service._api)
        transformer = self.mockDep(self._service._transformer)
        cache = self.mockDep(self._service._cache)

        self.mocker.patch.object(
            cache, "get", return_value=fullDf if isCacheHit else emptyDf
        )

        cachePutMock = self.mocker.patch.object(cache, "put")

        apiFetchMock = self.mocker.patch.object(
            api, "supportedGeographies", return_value=apiRetval
        )

        transGeoMock = self.mocker.patch.object(
            transformer, "supportedGeographies", return_value=transformerRetval
        )

        self._service.getSupportedGeographies()

        if isCacheHit:
            apiFetchMock.assert_not_called()
            transGeoMock.assert_not_called()
            cachePutMock.assert_not_called()
        else:
            apiFetchMock.assert_called_once()
            transGeoMock.assert_called_once_with(apiRetval)
            cachePutMock.assert_called_once_with(
                "supportedGeographies.csv", transformerRetval
            )

    def test_getGeographyCodes(self):
        forDomain = MagicMock()
        inDomains = [MagicMock()]

        api = self.mockDep(self._service._api)
        transformer = self.mockDep(self._service._transformer)

        apiGeoMock = self.mocker.patch.object(
            api, "geographyCodes", return_value=apiRetval
        )
        transMock = self.mocker.patch.object(
            transformer, "geographyCodes", return_value=transformerRetval
        )

        res = self._service.getGeographyCodes(
            forDomain, cast(List[GeoDomain], inDomains)
        )

        apiGeoMock.assert_called_once_with(forDomain, inDomains)
        transMock.assert_called_once_with(apiRetval)

        assert res == transformerRetval

    def test_getVariablesByGroup(self, monkeypatch: MonkeyPatch):
        cacheHitGroup = TGroupCode("hit")
        cacheMissGroup = TGroupCode("miss")

        transformer = self.mockDep(self._service._transformer)
        cache = self.mockDep(self._service._cache)

        monkeypatch.setattr(pandas, "DataFrame", lambda: emptyDf)

        self.mocker.patch.object(self._service, "_populateCodes")

        self.mocker.patch.object(transformer, "variables", return_value=fullDf)

        def cacheGetSideEffect(resource: str) -> pandas.DataFrame:
            return fullDf if cacheHitGroup in resource else emptyDf

        self.mocker.patch.object(cache, "get", side_effect=cacheGetSideEffect)

        self._service.getVariablesByGroup([cacheHitGroup, cacheMissGroup])
