from .client_api import RiotClient
from data.endpoints.endpoint import Endpoint
from models.summoner import Summoner
from .exceptions import RiotNotFoundError


class SummonerAPI:
    def __init__(self, client: RiotClient) -> None:
        self.client: RiotClient = client

    def get_summoner_riot_id_info(self, summoner_id: str) -> Summoner | None:
        endpoint: str = Endpoint.ACCOUNT_BY_RIOT_ID.format(
            summoner_id=summoner_id,
            tagline=self.client.tagline,
            api_riot=self.client.api_riot,
        )

        try:
            summoner_info = self.client._request(endpoint, routing="regional")

        except RiotNotFoundError:
            return None

        return Summoner(
            puuid=summoner_info["puuid"],
            game_name=summoner_info["gameName"],
            tag_line=summoner_info["tagLine"],
        )
