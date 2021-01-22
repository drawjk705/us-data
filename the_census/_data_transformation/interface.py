from abc import abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Generic, List, TypeVar

from the_census._api.models import GeographyItem
from the_census._geographies.models import GeoDomain
from the_census._variables.models import Group, GroupVariable, VariableCode

T = TypeVar("T")


class ICensusDataTransformer(Generic[T]):
    """
    This takes care of converting parsed API data
    into more meaningfully consumable data (e.g., DataFrames)
    """

    @abstractmethod
    def supported_geographies(
        self, supported_geos: OrderedDict[str, GeographyItem]
    ) -> T:
        ...

    @abstractmethod
    def geography_codes(self, geo_codes: List[List[str]]) -> T:
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
        type_conversions: Dict[str, Any],
        geo_domains_queried: List[GeoDomain],
        column_headers: Dict[VariableCode, str],
        supported_geos: T,
    ) -> T:
        """Parses stats data.

        This one get can get a bit complicated. Here's why:

        For stats, we might need to make batches API calls. This means
        that, when storing all of this in a DataFrame, we'll need to join
        on the geography IDs. This is why we pass in the geography domains
        which the stats service used to get the stats to the transformer.

        We can't rely on `results` for parsing out the geography columns,
        since `results` can have anywhere between 1 and 50 variables; and
        there's no way to know what portion of `results` is variables,
        and what portion is geography information.

        Args:
            results (List[List[List[str]]]): from the API
            type_conversions (Dict[str, Any]): for converting the data (which may all be strings) to
                floats if necessary, otherwise strings
            geo_domains_queried (List[str]): by the stats service
            column_headers (Dict[VariableCode, str]): the column headers with cleaned names
            supportedGoes (T): we need to pass this in (as opposed to DI-ing the Geography
                repo), since that would result in a circular dependency otherwise

        Returns:
            T: [description]
        """
        ...
