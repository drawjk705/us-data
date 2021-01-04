class CensusDoesNotExistException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidQueryException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)