from dataclasses import dataclass

@dataclass
class User:
    cursor: str = ""                # The cursor
    count: int = 0                  # The amount of badges the user has
    cursor_count: int = 0           # The amount of badges the user has before the cursor
    place: int = 0                  # Placing on the leaderboard
    counting: bool = False          # Whether the user is being counted without the cursor
    quick_counting: bool = False    # Whether the user is being counted with the cursor
    blacklisted: bool = False       # Whether the user is blacklisted
