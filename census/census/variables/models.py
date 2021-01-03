from dataclasses import dataclass
from typing import Any, Generator, Generic, Mapping, NewType, Tuple, TypeVar, Union


TVariableCode = NewType("TVariableCode", str)
TGroupCode = NewType("TGroupCode", str)


_TCode = TypeVar("_TCode", bound=Union[TVariableCode, TGroupCode])


@dataclass
class Code(Generic[_TCode]):
    code: _TCode
    meaning: str

    def __repr__(self) -> str:
        return {"code": self.code, "meaning": self.meaning}.__repr__()

    def __hash__(self) -> int:
        return hash(self.code) + hash(self.meaning)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self.code == o.code and self.meaning == o.meaning


@dataclass
class CodeSet(Generic[_TCode]):
    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        for k, v in kwargs.items():
            self.__setattr__(k, v)  # type: ignore

    # type: ignore
    def addCodes(self, **codes: Mapping[_TCode, Code[_TCode]]) -> None:
        for k, v in codes.items():
            self.__setattr__(k, v)  # type: ignore

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __len__(self) -> int:
        return len(self.__dict__)

    def __getitem__(self, code: str) -> Code[_TCode]:
        return self.__dict__[code]

    def items(self) -> Generator[Tuple[_TCode, Code[_TCode]], None, None]:
        for codeStr, codeObj in self.__dict__.items():
            yield codeStr, codeObj  # type: ignore

    def __hash__(self) -> int:
        return sum(hash(k) + hash(v) for k, v in self.__dict__.items())

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            return False

        return hash(self) == hash(o)
