from typing import Generic, Mapping, NewType, TypeVar, Union


TVariableCode = NewType("TVariableCode", str)
TGroupCode = NewType("TGroupCode", str)


_TCode = TypeVar("_TCode", bound=Union[TVariableCode, TGroupCode])


class Code(Generic[_TCode]):
    code: _TCode
    meaning: str

    def __init__(self, code: _TCode, meaning: str) -> None:
        self.code = code
        self.meaning = meaning

    def __repr__(self) -> str:
        return self.__dict__.__repr__()


class CodeSet(Generic[_TCode]):
    def __init__(self, **kwargs: dict) -> None:  # type: ignore
        for k, v in kwargs.items():
            self.__setattr__(k, v)  # type: ignore

    # type: ignore
    def addCodes(self, **codes: Mapping[str, _TCode]) -> None:
        for k, v in codes.items():
            self.__setattr__(k, v)  # type: ignore

    def __repr__(self) -> str:
        return self.__dict__.__repr__()
