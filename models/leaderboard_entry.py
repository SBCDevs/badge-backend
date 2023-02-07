from dataclasses import dataclass

@dataclass
class LeaderboardEntry:
    place: int
    count: int
    userId: int
    quick_counting: bool
    counting: bool
