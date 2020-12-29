class Domain:
    name: str
    codeOrWildcard: str

    def __init__(self, name: str, codeOrWildcard: str) -> None:
        self.name = name
        self.codeOrWildcard = codeOrWildcard

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'{self.name}:{self.codeOrWildcard}'
