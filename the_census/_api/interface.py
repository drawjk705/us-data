from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Generator, List

from the_census._api.models import GeographyItem
from the_census._geographies.models import GeoDomain
from the_census._variables.models import Group, GroupVariable, VariableCode


class ICensusApiFetchService(ABC):
    """
    Interface for our API client, which will
    perform all fetches for the Census API
    """

    @abstractmethod
    def healthcheck(self) -> None:
        """
        makes sure that the API client is
        configured properly
        """
        ...

    @abstractmethod
    def geography_codes(
        self, for_domain: GeoDomain, in_domains: List[GeoDomain] = []
    ) -> List[List[str]]:
        """
        Gets all geography codes for a given location domain:

        Args:
            for_domain (GeoDomain): the domain you want to search. This must
            be a child of any provided `in_domains`, as specified in the API's
            geography hierarchy.

            in_domains (List[GeoDomain], optional): geography domains
            that may help specify the query (e.g., if you want to
            search all congressional districts in a particular state).
            Defaults to [].

        Returns:
            List[List[str]]: API response
        """
        ...

    @abstractmethod
    def group_data(self) -> Dict[str, Group]:
        """
        Retrieves data on available concept groups for a given dataset/survey

        Returns:
            Dict[str, Group]: Mapping of group ID to concept
        """
        ...

    @abstractmethod
    def supported_geographies(self) -> OrderedDict[str, GeographyItem]:
        """
        Retrieves all queryable geographies for a given dataset/survey

        Returns:
            OrderedDict[str, GeographyItem]: mapping between a geography
            and possible queries that can be made on it
        """
        ...

    @abstractmethod
    def variables_for_group(self, group: str) -> List[GroupVariable]:
        """
        Gets all queryable variables for a survey group concept.

        Args:
            group (str): The group's code

        Returns:
            List[GroupVariable]
        """
        ...

    @abstractmethod
    def all_variables(self) -> List[GroupVariable]:
        """
        Gets all variables. This may be costly

        Returns:
            List[GroupVariable]: all of the variables.
        """
        ...

    @abstractmethod
    def stats(
        self,
        variables_codes: List[VariableCode],
        for_domain: GeoDomain,
        in_domains: List[GeoDomain] = [],
    ) -> Generator[List[List[str]], None, None]:
        """
        Gets stats based on `variableCodes` for the geographies in question.
        Returns a generator, since we may need to make repeat API
        calls due to limits on the number of variables (50) that the API
        will accept to query at a time.

        Args:
            variables_codes (List[VariableCode])
            for_domain (GeoDomain)
            in_domains (List[GeoDomain], optional). Defaults to [].

        Yields:
            Generator[List[List[str]], None, None]
        """
        ...


class ICensusApiSerializationService(ABC):
    """
    Serialization layer between the raw API results & models
    """

    @abstractmethod
    def parse_group_variables(self, group_variables: Any) -> List[GroupVariable]:
        """
        Parses an API response for variable retrieval

        Args:
            group_variables (Any): JSON response

        Returns:
            List[GroupVariable]:
        """

        ...

    @abstractmethod
    def parse_supported_geographies(
        self, supported_geos_response: Any
    ) -> OrderedDict[str, GeographyItem]:
        """
        parse a supported geographies response from the census API:

        Args:
            supported_geos_response (Any)

        Returns:
            OrderedDict[str, GeographyItem]: mapping the geography title to its name and code
        """

        ...

    @abstractmethod
    def parse_groups(
        self, groups_res: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Group]:
        """
        Parses a /groups.json response from the census API

        Args:
            groups_res (Dict[str, List[Dict[str, str]]])

        Returns:
            Dict[str, Group]
        """
        ...
