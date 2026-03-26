from dataclasses import dataclass


@dataclass
class MatchIds:
    tier: str
    match_ids: dict
