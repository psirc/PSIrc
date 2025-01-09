from enum import Enum, auto


class IdentityType(Enum):
    UNKNOWN = 0
    USER = auto()
    SERVER = auto()


class Identity:
    """Represents user or server.
    attributes:
        nick - ``str``, nick of user or server
        type - ``IdentityType``, server or user
    """
    def __init__(self) -> None:
        self.nick = ""
        self.type = IdentityType.UNKNOWN

    def registered(self) -> bool:
        return self.nick and self.type is not IdentityType.UNKNOWN
