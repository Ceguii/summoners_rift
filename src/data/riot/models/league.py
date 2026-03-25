from dataclasses import dataclass


@dataclass
class League:
    tier: str
    rank: str
    puuid: str
    league_points: int
    wins: int
    losses: int
