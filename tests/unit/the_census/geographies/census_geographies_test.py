from unittest.mock import MagicMock

import pandas
import pytest

from tests.serviceTestFixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from the_census._geographies.service import GeographyRepository

apiRetval = "banana"


class TestGeographyRepository(ServiceTestFixture[GeographyRepository]):
    @pytest.mark.parametrize(*shuffled_cases(isCacheHit=[True, False]))
    def test_get_supported_geographies(self, isCacheHit: bool):
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
            self._service._api, "supported_geographies", return_value=apiRetval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "supported_geographies", return_value=fullDf
        )

        self._service.get_supported_geographies()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.castMock(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(apiRetval)
            self.castMock(self._service._cache.put).assert_called_once_with(
                "supported_geographies.csv", fullDf
            )

    def test_get_geography_codes(self):
        for_domain = MagicMock()
        in_domains = [MagicMock()]

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
            self._service._api, "geography_codes", return_value=apiRetval
        )
        transform = self.mocker.patch.object(
            self._service._transformer, "geography_codes", return_value=fullDf
        )

        res = self._service.get_geography_codes(for_domain, *in_domains)

        apiFetch.assert_called_once_with(for_domain, in_domains)
        transform.assert_called_once_with(apiRetval)

        assert res.to_dict() == fullDf.to_dict()
