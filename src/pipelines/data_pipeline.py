import sys
import json
import time
import logging

from dataclasses import asdict

from src.data.riot.client_api import RiotClient
from src.data.riot.league_api import LeagueAPI
from src.data.riot.match_id_api import MatchIdAPI
from src.data.riot.match_api import MatchAPI

from src.data.riot.models.league import League
from src.data.riot.models.match_ids import MatchIds
from src.utils.setup_logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
logger.info("Logger initialized")


class DataPipeline:
    def __init__(self, api_riot: str) -> None:
        self.api_riot = api_riot
        self.riot_client = RiotClient(api_riot)
        self.league_api = LeagueAPI(self.riot_client)
        self.match_id_api = MatchIdAPI(self.riot_client, count=1)
        self.match_api = MatchAPI(self.riot_client)

    def run(self) -> None:
        logger.info("START - data pipeline...")
        pipeline_start_time = time.perf_counter()

        ########### Get all puuid from each league ###########
        ## leagues : [{tier, rank, puuid, PL, wins, losses}]
        start_leagues = time.perf_counter()
        leagues: list[dict[str, list[League]]] = self.league_api.run_leagues()
        end_leagues = time.perf_counter()
        logger.info(f"RESULT - fetched {len(leagues)} league tiers/divisions")
        logger.info(
            f"EXECUTION TIME - fetched league - {end_leagues - start_leagues:.4f} secondes"
        )

        with open("data_riot/raw/leagues.json", "w", encoding="utf-8") as file:
            json.dump(leagues, file, indent=4, default=lambda o: asdict(o))

        ########### Get all match from each puuid ###########
        start_match_id = time.perf_counter()
        tier_match_ids: list[MatchIds] = (
            self.match_id_api.get_list_match_ids_for_all_puuid(leagues)
        )
        end_match_id = time.perf_counter()
        logger.info(f"RESULT - fetched {len(tier_match_ids)} match id")
        logger.info(
            f"EXECUTION TIME - fetched match ids - {end_match_id - start_match_id:.4f} secondes"
        )

        with open("data_riot/raw/match_ids.json", "w", encoding="utf-8") as file:
            json.dump(tier_match_ids, file, indent=4, default=lambda o: asdict(o))

        ########### Get match details for each match id ###########
        start_extract_match_detail = time.perf_counter()
        match_details = self.match_api.get_all_match(tier_match_ids)
        end_extract_match_detail = time.perf_counter()
        logger.info(f"RESULT - fetched {len(match_details)} match details")

        logger.info(
            f"EXECUTION TIME - fetched match details - {end_extract_match_detail - start_extract_match_detail:.4f} secondes"
        )

        with open(
            "data_riot/raw/match_details_parsed.json", "w", encoding="utf-8"
        ) as file:
            json.dump(match_details, file, indent=4, default=lambda o: asdict(o))

        pipeline_end_time = time.perf_counter()
        logger.info(
            f"EXECUTION TIME - data pipeline - {pipeline_end_time - pipeline_start_time:.4f} secondes"
        )
        logger.info("END - data pipeline...")
