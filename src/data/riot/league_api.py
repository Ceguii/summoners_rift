import json

from dataclasses import asdict

from src.data.riot.client_api import RiotClient
from src.data.enums.division import Division
from src.data.enums.tier import Tier
from src.data.enums.queue import Queue
from src.data.endpoints.endpoint import Endpoint
from src.data.riot.exceptions import RiotNotFoundError
from src.data.riot.models.league import League


class LeagueAPI:
    TOP_TIERS_ = [
        Tier.CHALLENGER,
        Tier.GRANDMASTER,
        Tier.MASTER,
    ]

    ENTRIE_TIERS_ = [
        Tier.DIAMOND,
        Tier.EMERALD,
        Tier.PLATINUM,
        Tier.GOLD,
        Tier.SILVER,
        Tier.BRONZE,
        Tier.IRON,
    ]

    DIVISIONS_ = [
        Division.I,
        Division.II,
        Division.III,
        Division.IV,
    ]

    def __init__(self, client: RiotClient) -> None:
        self.client = client

    def endpoint_handler(
        self, queue: Queue, tier: Tier, division: Division | None = None
    ) -> str:
        if tier == Tier.CHALLENGER:
            endpoint = Endpoint.CHALLENGER_LEAGUE.format(
                queue=queue.value, api_riot=self.client.api_riot
            )
        elif tier == Tier.GRANDMASTER:
            endpoint = Endpoint.GRANDMASTER_LEAGUE.format(
                queue=queue.value, api_riot=self.client.api_riot
            )
        elif tier == Tier.MASTER:
            endpoint = Endpoint.MASTER_LEAGUE.format(
                queue=queue.value, api_riot=self.client.api_riot
            )
        else:
            if division is None:
                raise ValueError("division must be provided for this tier")

            endpoint = Endpoint.ENTRIES_LEAGUE_BY_TIER_DIVISION.format(
                queue=queue.value,
                tier=tier.value,
                division=division.value,
                page=1,
                api_riot=self.client.api_riot,
            )

        return endpoint

    def get_top_leagues(self, endpoint: str) -> list[League]:
        try:
            responses: dict | None = self.client._request(endpoint, routing="platform")

        except RiotNotFoundError:
            raise RuntimeError(f"No league data returned for endpoits {endpoint}")

        leagues: list[League] = []
        for items in responses["entries"]:
            league = League(
                tier=responses["tier"],
                rank=items["rank"],
                puuid=items["puuid"],
                league_points=items["leaguePoints"],
                wins=items["wins"],
                losses=items["losses"],
            )
            leagues.append(league)
            
        return leagues

    def get_entries_leagues(self, endpoint: str) -> list[League]:
        try:
            responses: dict | None = self.client._request(endpoint, routing="platform")

        except RiotNotFoundError:
            raise RuntimeError(f"No league data returned for endpoits {endpoint}")

        leagues: list[League] = []
        for response in responses:
            league = League(
                tier=response["tier"],
                rank=response["rank"],
                puuid=response["puuid"],
                league_points=response["leaguePoints"],
                wins=response["wins"],
                losses=response["losses"],
            )
            leagues.append(league)
            
        return leagues

    def run_leagues(self) -> list[dict]:
        leagues: list[dict] = []

        # top tiers rank
        for tier in self.TOP_TIERS_:
            league_divisions: dict[str, list[League]] = {}

            league: list[League] | None = self.get_top_leagues(
                self.endpoint_handler(Queue.RANKED_SOLO, tier)
            )
            if league is None:
                raise RuntimeError(f"No league data returned for {tier.value}")

            league_divisions[f"{tier.value}"] = league
            leagues.append(league_divisions)

        # entrie tiers rank
        for tier in self.ENTRIE_TIERS_:
            league_divisions: dict[str, list[League]] = {}

            for division in self.DIVISIONS_:
                league: list[League] | None = self.get_entries_leagues(
                    self.endpoint_handler(Queue.RANKED_SOLO, tier, division)
                )
                if league is None:
                    raise RuntimeError(f"No league data returned for {tier.value}")

                league_divisions[f"{tier.value}_{division.value}"] = league

            leagues.append(league_divisions)

        with open("data_riot/raw/leagues.json", "w", encoding="utf-8") as file:
            json.dump(leagues, file, indent=4, default=lambda o: asdict(o))
            
        return leagues
