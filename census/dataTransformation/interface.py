from abc import abstractmethod
from census.geographies.models import GeoDomain
from collections import OrderedDict
from census.variables.models import Group, GroupVariable, VariableCode
from census.api.models import GeographyItem
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class ICensusDataTransformer(Generic[T]):
    """
    This takes care of converting parsed API data
    into more meaningfully consumable data (e.g., DataFrames)
    """

    @abstractmethod
    def supportedGeographies(self, supportedGeos: OrderedDict[str, GeographyItem]) -> T:
        ...

    @abstractmethod
    def geographyCodes(self, geoCodes: List[List[str]]) -> T:
        ...

    @abstractmethod
    def groups(self, groups: Dict[str, Group]) -> T:
        ...

    @abstractmethod
    def variables(self, variables: List[GroupVariable]) -> T:
        ...

    @abstractmethod
    def stats(
        self,
        results: List[List[List[str]]],
        typeConversions: Dict[str, Any],
        geoDomains: List[GeoDomain],
        columnHeaders: Optional[Dict[VariableCode, str]],
    ) -> T:
        ...
