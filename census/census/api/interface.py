from abc import ABC, abstractmethod
from typing import Any, Dict, List, OrderedDict
from census.models import GeoDomain
from census.api.models import GeographyItem, Group, GroupVariable


class IApiFetchService(ABC):
    @abstractmethod
    def geographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> Any:
        pass

    @abstractmethod
    def groupData(self) -> Dict[str, Group]:
        pass

    @abstractmethod
    def supportedGeographies(self) -> OrderedDict[str, GeographyItem]:
        pass

    @abstractmethod
    def variablesForGroup(self, group: str) -> List[GroupVariable]:
        pass

    @abstractmethod
    def stats(
        self,
        variables: List[GroupVariable],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> Any:
        pass


class IApiSerializationService(ABC):
    @abstractmethod
    def parseVariableData(self, variableData: Any) -> List[GroupVariable]:
        pass

    @abstractmethod
    def parseSupportedGeographies(
        self, supportedGeosResponse: Any
    ) -> OrderedDict[str, GeographyItem]:
        pass

    @abstractmethod
    def parseGroups(
        self, groupsRes: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Group]:
        pass