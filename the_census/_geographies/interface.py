from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from the_census._geographies.models import GeoDomain, SupportedGeoSet

T = TypeVar("T")


class IGeographyRepository(ABC, Generic[T]):
    """
    Gets and stores all geography information
    """

    _supportedGeographies: SupportedGeoSet

    @abstractmethod
    def getSupportedGeographies(self) -> T:
        ...

    @abstractmethod
    def getGeographyCodes(self, forDomain: GeoDomain, *inDomains: GeoDomain) -> T:
        ...

    @property
    def supportedGeographies(self) -> SupportedGeoSet:
        return self._supportedGeographies
