from src.data.riot.client_api import RiotClient
from src.data.endpoints.endpoint import Endpoint
from src.data.riot.exceptions import RiotNotFoundError
from src.data.enums.team import Team
from src.data.riot.models.match_ids import MatchIds


class MatchAPI:
    BLUE_TEAM = set(range(1, 6))
    RED_TEAM = set(range(6, 11))

    def __init__(self, client: RiotClient) -> None:
        self.client = client

    def get_team(self, participant_id: int):
        return (
            Team.BLUE_TEAM.value
            if participant_id in MatchAPI.BLUE_TEAM
            else Team.RED_TEAM.value
        )

    def init_match_details_data(self) -> dict:
        return {
            Team.BLUE_TEAM.value: self.init_match_details(),
            Team.RED_TEAM.value: self.init_match_details(),
        }

    def init_match_details(self) -> dict:
        return {
            "TOTAL_GOLD": 0,
            "TOTAL_LEVEL": 0,
            "TOTAL_MINION_KILLED": 0,
            "TOTAL_JUNGLE_MINION_KILLED": 0,
            "GOLD_PER_MINUTE": 0,  # data engineering
            "CS_PER_MINUTE": 0,  # data engineering
            "WARD_PLACED": 0,
            "WARD_KILL": 0,
            "FIRST_BLOOD": False,
            "CHAMPION_KILL": 0,
            "DEATH": 0,
            "ASSISTING": 0,
            "BUILDING_KILL": 0,
            "ELITE_MONSTER_KILL": {
                "HORDE": 0,
                "DRAGON": 0,
                "RIFTHERALD": 0,
                "NASHOR": 0,
            },
        }

    def extract_match_ids(self, tier_match_ids: list[MatchIds]) -> list:
        final_match_ids = []
        for items in tier_match_ids:
            match_ids = items.match_ids
            for match_id in match_ids:
                final_match_ids.append(match_id)

        return final_match_ids

    def parse_events(self, data: dict, events: list) -> None:
        for event in events:
            # type : WARD_PLACED
            if event["type"] == "WARD_PLACED" and event["wardType"] != "UNDEFINED":
                team = self.get_team(event["creatorId"])
                data[team]["WARD_PLACED"] += 1

            # type : WARD_KILL
            if event["type"] == "WARD_KILL":
                team = self.get_team(event["killerId"])
                data[team]["WARD_KILL"] += 1

            # type : CHAMPION_SPECIAL_KILL (first blood)
            if event["type"] == "CHAMPION_SPECIAL_KILL":
                team = self.get_team(event["killerId"])
                data[team]["FIRST_BLOOD"] = True

            # type : CHAMPION KILL
            if event["type"] == "CHAMPION_KILL":
                killer_team = self.get_team(event["killerId"])
                victim_team = (
                    Team.RED_TEAM.value
                    if killer_team == Team.BLUE_TEAM.value
                    else Team.BLUE_TEAM.value
                )

                data[killer_team]["CHAMPION_KILL"] += 1
                data[killer_team]["ASSISTING"] += len(
                    event.get("assistingParticipantIds", [])
                )
                data[victim_team]["DEATH"] += 1

            # type : BUILDING_KILL
            if event["type"] == "BUILDING_KILL":
                team = self.get_team(event["killerId"])
                data[team]["BUILDING_KILL"] += 1

            # type : ELITE_MONSTER_KILL
            if event["type"] == "ELITE_MONSTER_KILL":
                team = self.get_team(event["killerId"])
                monster = event.get("monsterType", "NASHOR")

                if monster not in data[team]["ELITE_MONSTER_KILL"]:
                    monster = "NASHOR"

                data[team]["ELITE_MONSTER_KILL"][monster] += 1

    def parse_participant_frames(self, data: dict, participant_frames: dict) -> None:
        for participant, frame in participant_frames.items():
            team = self.get_team(int(participant))

            data[team]["TOTAL_LEVEL"] += frame["level"]
            data[team]["TOTAL_GOLD"] += frame["totalGold"]
            data[team]["TOTAL_MINION_KILLED"] += frame["minionsKilled"]
            data[team]["TOTAL_JUNGLE_MINION_KILLED"] += frame["jungleMinionsKilled"]

    def single_match_details(self, match_id: str) -> dict | None:
        endpoint = Endpoint.MATCH_DETAILS_TIMELINE_USING_MATCH_ID.format(
            match_id=match_id, api_riot=self.client.api_riot
        )

        try:
            match_details = self.client._request(endpoint, routing="regional")
            return match_details

        except RiotNotFoundError:
            return None

    def match_details_parsing(self, match_detail: dict) -> dict:

        data = self.init_match_details_data()
        frames = match_detail["info"]["frames"]
        # match_metadata = match_detail["metadata"]

        for frame in frames:
            self.parse_events(data, frame["events"])

            # take the last frame at 15 minutes
            if frame["timestamp"] >= 900000:
                self.parse_participant_frames(data, frame["participantFrames"])
                break

        return data

    def get_all_match(self, tier_match_ids: list[MatchIds]) -> list:
        match_ids = self.extract_match_ids(tier_match_ids)

        matches = []
        for match_id in match_ids:
            match_details = self.single_match_details(match_id)

            if match_details is None:
                continue

            matches.append(self.match_details_parsing(match_details))

        return matches
