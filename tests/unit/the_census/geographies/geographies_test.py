from unittest.mock import MagicMock

import pandas
import pytest

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from the_census._geographies.service import GeographyRepository

api_retval = "banana"


class TestGeographyRepository(ServiceTestFixture[GeographyRepository]):
    @pytest.mark.parametrize(*shuffled_cases(isCacheHit=[True, False]))
    def test_get_supported_geographies(self, isCacheHit: bool):
        full_df = pandas.DataFrame(
            [
                {"name": "us", "hierarchy": 1, "for": "this", "in": "that"},
                {"name": "them", "hierarchy": 2, "for": "that", "in": "this"},
            ]
        )

        self.mocker.patch.object(
            self._service._cache, "get", return_value=full_df if isCacheHit else None
        )
        apiFetch = self.mocker.patch.object(
            self._service._api, "supported_geographies", return_value=api_retval
        )

        transform = self.mocker.patch.object(
            self._service._transformer, "supported_geographies", return_value=full_df
        )

        self._service.get_supported_geographies()

        if isCacheHit:
            apiFetch.assert_not_called()
            transform.assert_not_called()
            self.cast_mock(self._service._cache.put).assert_not_called()
        else:
            apiFetch.assert_called_once()
            transform.assert_called_once_with(api_retval)
            self.cast_mock(self._service._cache.put).assert_called_once_with(
                "supported_geographies.csv", full_df
            )

    def test_get_geography_codes(self):
        for_domain = MagicMock()
        in_domains = [MagicMock()]

        full_df = pandas.DataFrame(
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

        api_fetch = self.mocker.patch.object(
            self._service._api, "geography_codes", return_value=api_retval
        )
        transform = self.mocker.patch.object(
            self._service._transformer, "geography_codes", return_value=full_df
        )

        res = self._service.get_geography_codes(for_domain, *in_domains)

        api_fetch.assert_called_once_with(for_domain, in_domains)
        transform.assert_called_once_with(api_retval)

        assert res.to_dict() == full_df.to_dict()
