import logging

from src.data.riot.client_api import RiotClient
from src.data.endpoints.endpoint import Endpoint
from src.data.riot.exceptions import RiotNotFoundError
from src.data.riot.models.league import League
from src.data.riot.models.match_ids import MatchIds

logger = logging.getLogger(__name__)


class MatchIdAPI:
    def __init__(
        self,
        client: RiotClient,
        start_time: int | None = None,
        end_time: int | None = None,
        queue: int | None = None,
        type: str = "ranked",
        start: int = 0,
        count: int = 20,
    ) -> None:

        self.client = client
        self.start_time = start_time
        self.end_time = end_time
        self.queue = queue
        self.type = type
        self.start = start
        self.count = count

        if self.count < 0 and self.count > 100:
            raise ValueError(
                "defaults to 20, valid values: 0 to 100, number of match ids to return..."
            )

    def get_list_match_ids_single_puuid(self, tier: str, puuid: str) -> MatchIds | None:
        endpoint = Endpoint.MATCH_IDS_BY_PUUID.format(
            puuid=puuid,
            type=self.type,
            start=self.start,
            count=self.count,
            api_riot=self.client.api_riot,
        )

        try:
            match_ids = self.client._request(endpoint, routing="regional")
            return MatchIds(tier=tier, match_ids=match_ids)

        except RiotNotFoundError:
            return None

    def get_list_match_ids_for_all_puuid(
        self, leagues: list[dict[str, list[League]]]
    ) -> list[MatchIds]:
        all_match_ids: list[MatchIds] = []
        logger.info("START - fetch all match ids")

        for league in leagues:
            for tier, player_infos in league.items():
                logger.debug(f"CURRENT STATE - tier - {tier}")
                current_puuid = 1

                for player_info in player_infos:
                    match_ids = self.get_list_match_ids_single_puuid(
                        tier, player_info.puuid
                    )
                    logger.debug(
                        f"CURRENT STATE - puuid/tot_puuids - {current_puuid}/{len(player_infos)}"
                    )
                    current_puuid += 1

                    if match_ids is None:
                        continue

                    all_match_ids.append(match_ids)

        logger.info("END - fetch all match ids")
        return all_match_ids
