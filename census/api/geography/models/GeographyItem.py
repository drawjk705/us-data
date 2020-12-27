from typing import List, Set


class GeographyClauses:
    forClause: str = ''
    inClauses: List[str] = []

    def __init__(self, forClause: str, inClauses: List[str]) -> None:
        self.forClause = forClause
        self.inClauses = inClauses

    def __eq__(self, o: object) -> bool:
        return \
            self.forClause == o.__getattribute__('forClause') \
            and self.inClauses == o.__getattribute__('inClauses')

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __hash__(self) -> int:
        return self.forClause.__hash__() + \
            sum([item.__hash__() for item in self. inClauses])


class GeographyItem:

    name: str
    hierarchy: str
    clauses: Set[GeographyClauses] = {}
    hierarchy: str

    def __init__(self, name: str, hierarchy: str, clauses: Set[GeographyClauses]) -> None:
        self.name = name
        self.hierarchy = hierarchy
        self.clauses = clauses

    def __eq__(self, o: object) -> bool:
        return \
            self.name == o.__getattribute__('name') and \
            self.hierarchy == o.__getattribute__('hierarchy') and \
            self.clauses == o.__getattribute__('clauses')

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __hash__(self) -> int:
        return self.name.__hash__() + self.hierarchy.__hash__() + self.clauses.__hash__()
