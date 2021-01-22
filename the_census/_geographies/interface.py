from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from the_census._geographies.models import GeoDomain, SupportedGeoSet

T = TypeVar("T")


class IGeographyRepository(ABC, Generic[T]):
    """
    Gets and stores all geography information
    """

    _supported_geographies: SupportedGeoSet

    @abstractmethod
    def get_supported_geographies(self) -> T:
        ...

    @abstractmethod
    def get_geography_codes(self, for_domain: GeoDomain, *in_domains: GeoDomain) -> T:
        ...

    @property
    def supported_geographies(self) -> SupportedGeoSet:
        return self._supported_geographies
