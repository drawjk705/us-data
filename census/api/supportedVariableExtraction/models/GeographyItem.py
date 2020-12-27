from typing import Generator, List, Tuple


class GeographyItem:
    forClause: str = ''
    inClauses: List[str] = []

    def __init__(self, forClause: str, inClauses: List[str]) -> None:
        self.forClause = forClause
        self.inClauses = inClauses

    def __eq__(self, o: object) -> bool:
        return self.forClause == o.__getattribute__('forClause') and self.inClauses == o.__getattribute__('inClauses')

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __hash__(self) -> int:
        return self.forClause.__hash__() + sum([item.__hash__() for item in self. inClauses])
