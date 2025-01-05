from enum import Enum, auto


class IRCCommand(Enum):
    PASS = 1000
    NICK = auto()
    USER = auto()
    JOIN = auto()
