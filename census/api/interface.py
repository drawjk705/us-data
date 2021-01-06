from abc import ABC, abstractmethod
from census.variables.models import Group, GroupVariable, VariableCode
from typing import Any, Dict, Generator, List
from collections import OrderedDict
from census.models import GeoDomain
from census.api.models import GeographyItem


class IApiFetchService(ABC):
    """
    Interface for our API client, which will
    perform all fetches for the Census API
    """

    @abstractmethod
    def healthCheck(self) -> None:
        """
        makes sure that the API client is
        configured properly
        """
        pass

    @abstractmethod
    def geographyCodes(
        self, forDomain: GeoDomain, inDomains: List[GeoDomain] = []
    ) -> List[List[str]]:
        """
        Gets all geography codes for a given location domain:

        Args:
            forDomain (GeoDomain): the domain you want to search. This must
            be a child of any provided `inDomains`, as specified in the API's
            geography hierarchy.

            inDomains (List[GeoDomain], optional): geography domains
            that may help specify the query (e.g., if you want to
            search all congressional districts in a particular state).
            Defaults to [].

        Returns:
            List[List[str]]: API response
        """
        pass

    @abstractmethod
    def groupData(self) -> Dict[str, Group]:
        """
        Retrieves data on available concept groups for a given dataset/survey

        Returns:
            Dict[str, Group]: Mapping of group ID to concept
        """
        pass

    @abstractmethod
    def supportedGeographies(self) -> OrderedDict[str, GeographyItem]:
        """
        Retrieves all queryable geographies for a given dataset/survey

        Returns:
            OrderedDict[str, GeographyItem]: mapping between a geography
            and possible queries that can be made on it
        """
        pass

    @abstractmethod
    def variablesForGroup(self, group: str) -> List[GroupVariable]:
        """
        Gets all queryable variables for a survey group concept.

        Args:
            group (str): The group's code

        Returns:
            List[GroupVariable]
        """
        pass

    @abstractmethod
    def allVariables(self) -> List[GroupVariable]:
        """
        Gets all variables. This may be costly

        Returns:
            List[GroupVariable]: all of the variables.
        """
        pass

    @abstractmethod
    def stats(
        self,
        variablesCodes: List[VariableCode],
        forDomain: GeoDomain,
        inDomains: List[GeoDomain] = [],
    ) -> Generator[List[List[str]], None, None]:
        """
        Gets stats based on `variableCodes` for the geographies in question.
        Returns a generator, since we may need to make repeat API
        calls due to limits on the number of variables (50) that the API
        will accept to query at a time.

        Args:
            variablesCodes (List[VariableCode])
            forDomain (GeoDomain)
            inDomains (List[GeoDomain], optional). Defaults to [].

        Yields:
            Generator[List[List[str]], None, None]
        """
        pass


class IApiSerializationService(ABC):
    """
    Serialization layer between the raw API results & models
    """

    @abstractmethod
    def parseGroupVariables(self, groupVariables: Any) -> List[GroupVariable]:
        """
        Parses an API response for variable retrieval, e.g.:

        ```
        {
            "variables": {
                "B01001_047EA": {
                    "label": "Annotation of Estimate!!Total:!!Female:!!75 to 79 years",
                    "concept": "SEX BY AGE",
                    "predicateType": "string",
                    "group": "B01001",
                    "limit": 0,
                    "predicateOnly": true
                },
                "B01001_047MA": {
                    "label": "Annotation of Margin of Error!!Total:!!Female:!!75 to 79 years",
                    "concept": "SEX BY AGE",
                    "predicateType": "string",
                    "group": "B01001",
                    "limit": 0,
                    "predicateOnly": true
                }
            }
        },
        ```

        Args:
            variableData (Any): JSON response

        Returns:
            List[GroupVariable]:
        """

        pass

    @abstractmethod
    def parseSupportedGeographies(
        self, supportedGeosResponse: Any
    ) -> OrderedDict[str, GeographyItem]:
        """
        parse a supported geographies response from the census API, e.g.:

        ```
            {
                "default": [
                    {
                        "isDefault": "true"
                    }
                ],
                "fips": [
                    {
                        "name": "state",
                        "geoLevelDisplay": "040",
                        "referenceDate": "2019-01-01"
                    },
                    {
                        "name": "county",
                        "geoLevelDisplay": "050",
                        "referenceDate": "2019-01-01",
                        "requires": [
                            "state"
                        ],
                        "wildcard": [
                            "state"
                        ],
                        "optionalWithWCFor": "state"
                    },
                    {
                        "name": "principal city (or part)",
                        "geoLevelDisplay": "312",
                        "referenceDate": "2019-01-01",
                        "requires": [
                            "metropolitan statistical area/micropolitan statistical area",
                            "state (or part)"
                        ]
                    },
                ]
            }
        ```

        Args:
            supportedGeosResponse (Any)

        Returns:
            OrderedDict[str, GeographyItem]: mapping the geography title to its name and code
        """

        pass

    @abstractmethod
    def parseGroups(
        self, groupsRes: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, Group]:
        """
        Parses a /groups.json response from the census API, e.g.:

        ```
        {
            "groups": [
                {
                    "name": "B17015",
                    "description": "POVERTY STATUS IN THE PAST 12 MONTHS OF FAMILIES BY FAMILY TYPE BY SOCIAL SECURITY INCOME BY SUPPLEMENTAL SECURITY INCOME (SSI) AND CASH PUBLIC ASSISTANCE INCOME",
                    "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B17015.json"
                },
                {
                    "name": "B18104",
                    "description": "SEX BY AGE BY COGNITIVE DIFFICULTY",
                    "variables": "https://api.census.gov/data/2019/acs/acs1/groups/B18104.json"
                },
        }

        ```

        Args:
            groupsRes (Dict[str, List[Dict[str, str]]])

        Returns:
            Dict[str, Group]
        """
        pass