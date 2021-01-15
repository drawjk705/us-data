from unittest.mock import MagicMock

import pandas
import pytest

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import shuffledCases
from us_data.census._geographies.service import GeographyRepository

apiRetval = "banana"


class TestGeographyRepository(ServiceTestFixture[GeographyRepository]):
    @pytest.mark.parametrize(*shuffledCases(isCacheHit=[True, False]))
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
            self.castMock(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.castMock(self._service._cache.put).assert_called_once_with(
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

        res = self._service.getGeographyCodes(forDomain, *inDomains)

        apiFetch.assert_called_once_with(forDomain, inDomains)
        transform.assert_called_once_with(apiRetval)

        assert res.to_dict() == fullDf.to_dict()
