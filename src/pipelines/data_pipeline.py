from src.data.riot.client_api import RiotClient
from src.data.riot.league_api import LeagueAPI


class DataPipeline:
    def __init__(self, api_riot: str) -> None:
        self.api_riot = api_riot

    def run(self) -> None:

        riot_client = RiotClient(self.api_riot)
        league_api = LeagueAPI(riot_client)

        # Get all puuid from each league
        leagues = league_api.run_leagues()
        for league in leagues:
            for tier, info in league.items():
                print(f"{tier} - {len(info)}")
