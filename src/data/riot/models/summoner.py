from dataclasses import dataclass


@dataclass
class Summoner:
    puuid: str
    game_name: str
    tag_line: str
