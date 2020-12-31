from abc import abstractmethod
from census.variableRetrieval.models import VariableCodes
from typing import Generic, List, TypeVar
from census.models import GeoDomain

T = TypeVar("T")


class IVariableRetrievalService(Generic[T]):
    # these will be useful for jupyter
    variableCodes: VariableCodes
    groupCodes: VariableCodes

    @abstractmethod
    def getGroups(self) -> T:
        pass

    @abstractmethod
    def getSupportedGeographies(self) -> T:
        pass

    @abstractmethod
    def getGeographyCodes(self, forDomain: GeoDomain, inDomains: List[GeoDomain]) -> T:
        pass

    @abstractmethod
    def getVariablesByGroup(self, groups: List[str]) -> T:
        pass