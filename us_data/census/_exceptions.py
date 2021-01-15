class CensusDoesNotExistException(Exception):
    """
    Thrown during the healthcheck if the requested
    dataset/survey does not exist.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidQueryException(Exception):
    """
    Thrown if an invalid query was made to the Census API.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmptyRepositoryException(Exception):
    """
    Thrown when trying to make a query on variables
    whose metadata is not in the repository
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NoCensusApiKeyException(Exception):
    """
    Thrown when no Census API key is provided
    """
