from congress.config import CongressConfig
from congress.api.fetch import CongressApiFetchService
from tests.serviceTestFixtures import ApiServiceTestFixture

apiKey = "apiKey"
config = CongressConfig(116, apiKey)


class DummyApiService(CongressApiFetchService):
    def __init__(self) -> None:
        super().__init__(config)


class TestCongressApiFetch(ApiServiceTestFixture[DummyApiService]):
    def test_getRepresentatives_callsCorrectEndpoint(self):
        pass