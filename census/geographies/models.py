from census.utils.cleanVariableName import cleanVariableName


class SupportedGeoSet:
    def __init__(self) -> None:
        super().__init__()

    def add(self, *geoName: str):
        mapping = {cleanVariableName(name): name for name in geoName}
        self.__dict__.update(mapping)