class GroupVariable:
    code: str
    groupCode: str
    groupConcept: str
    name: str
    limit: int
    predicateOnly: bool
    predicateType: str

    def __init__(self, code: str, jsonData: dict) -> None:  # type: ignore
        self.code = code
        self.groupCode = jsonData['group']
        self.groupConcept = jsonData['concept']
        self.name = jsonData['label']
        self.limit = jsonData['limit']
        self.predicateOnly = jsonData['predicateOnly']
        self.predicateType = jsonData['predicateType']

    def __repr__(self) -> str:
        return self.__dict__.__repr__()
