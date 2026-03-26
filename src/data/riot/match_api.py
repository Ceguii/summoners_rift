from src.data.riot.client_api import RiotClient

class MatchAPI:
    def __init__(self, client: RiotClient) -> None:
        self.client = client
        pass
    
    def get_single_match(self) -> None:
        pass
    
    def get_all_match(self) -> None:
        pass