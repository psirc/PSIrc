from enum import Enum, auto


class IdentityType(Enum):
    UNKNOWN = 0
    CLIENT = auto()
    SERVER = auto()


class Identity:
    def __init__(self) -> None:
        self.nick = ""
        self.type = IdentityType.UNKNOWN

    def registered(self) -> bool:
        return self.nick and self.type is not IdentityType.UNKNOWN
