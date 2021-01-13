from abc import ABC, abstractmethod
from census.geographies.models import SupportedGeoSet
from typing import Generic, TypeVar
from census.geographies.models import GeoDomain

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
