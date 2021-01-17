from dataclasses import dataclass, field

from the_census._utils.cleanVariableName import cleanVariableName


@dataclass(frozen=True)
class GeoDomain:
    name: str
    codeOrWildcard: str = field(default="*")

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}:{self.codeOrWildcard}"


class SupportedGeoSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, *geoName: str):
        mapping = {cleanVariableName(name): name for name in geoName}
        self.__dict__.update(mapping)
