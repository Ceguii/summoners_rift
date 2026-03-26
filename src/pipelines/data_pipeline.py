import json

from dataclasses import asdict

from src.data.riot.client_api import RiotClient
from src.data.riot.league_api import LeagueAPI
from src.data.riot.match_id_api import MatchIdAPI

from src.data.riot.models.league import League
from src.data.riot.models.match_ids import MatchIds


class DataPipeline:
    def __init__(self, api_riot: str) -> None:
        self.api_riot = api_riot

    def run(self) -> None:

        riot_client = RiotClient(self.api_riot)
        league_api = LeagueAPI(riot_client)
        match_id_api = MatchIdAPI(riot_client)

        # Get all puuid from each league
        leagues: list[dict[str, list[League]]] = league_api.run_leagues()

        with open("data_riot/raw/leagues.json", "w", encoding="utf-8") as file:
            json.dump(leagues, file, indent=4, default=lambda o: asdict(o))

        for league in leagues:
            for tier, info in league.items():
                print(f"{tier} - {len(info)}")

        # Get all match (50) from each puuid
        match_ids: list[MatchIds] = match_id_api.get_list_match_ids_for_all_puuid(
            leagues
        )

        with open("data_riot/raw/match_ids.json", "w", encoding="utf-8") as file:
            json.dump(match_ids, file, indent=4, default=lambda o: asdict(o))

        for match_id in match_ids:
            print(f"tier : {match_id.tier} - match_ids : {match_id.match_ids}")
