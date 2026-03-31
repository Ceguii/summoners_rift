import logging

from dataclasses import asdict

from src.data.riot.client_api import RiotClient
from src.data.enums.division import Division
from src.data.enums.tier import Tier
from src.data.enums.queue import Queue
from src.data.endpoints.endpoint import Endpoint
from src.data.riot.exceptions import RiotNotFoundError
from src.data.riot.models.league import League

logger = logging.getLogger(__name__)


class LeagueAPI:
    TOP_TIERS_ = [
        Tier.CHALLENGER,
        # Tier.GRANDMASTER,
        # Tier.MASTER,
    ]

    ENTRIE_TIERS_ = [
        Tier.DIAMOND,
        Tier.EMERALD,
        # Tier.PLATINUM,
        # Tier.GOLD,
        # Tier.SILVER,
        # Tier.BRONZE,
        # Tier.IRON,
    ]

    DIVISIONS_ = [
        Division.I,
        # Division.II,
        # Division.III,
        # Division.IV,
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

    def get_single_league(
        self, queue: Queue, tier: Tier, division: Division | None = None
    ) -> list[League]:

        endpoint = self.endpoint_handler(queue, tier, division)

        if tier in self.TOP_TIERS_:
            return self.get_top_leagues(endpoint)
        else:
            return self.get_entries_leagues(endpoint)

    def run_leagues(self) -> list[dict[str, list[League]]]:
        leagues: list[dict] = []

        logger.info("START - fetch all top tier/division")
        for tier in self.TOP_TIERS_:
            league = self.get_single_league(Queue.RANKED_SOLO, tier)
            leagues.append({tier.value: league})
            logger.debug(f"CURRENT STATE - {tier.value}")

        logger.info("START - fetch all entries tier/division...")
        for tier in self.ENTRIE_TIERS_:
            league_divisions = {}
            for division in self.DIVISIONS_:
                league = self.get_single_league(Queue.RANKED_SOLO, tier, division)
                league_divisions[f"{tier.value}_{division.value}"] = league
                logger.debug(f"CURRENT STATE - {tier.value}/{division.value}")

            leagues.append(league_divisions)

        logger.info("END - fetch all tier/division")
        return leagues
