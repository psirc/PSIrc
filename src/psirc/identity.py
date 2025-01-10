from enum import Enum, auto


class IdentityType(Enum):
    UNKNOWN = 0
    USER = auto()
    SERVER = auto()

    def __str__(self) -> str:
        return self.name


class Identity:
    """Represents user or server.
    attributes:
        type - ``IdentityType``, server or user
        nickname - ``str``, nick of user or server
        password - ``str``, set password, which will be used to register user
        username - ``str``, username
        realname - ``str``, real name of user - contains space
    """

    def __init__(self, password: str) -> None:
        self.password = password
        self.nickname = ""
        self.username = ""
        self.realname = ""
        self.type = IdentityType.UNKNOWN

    def registered(self) -> bool:
        return self.nickname and self.type is not IdentityType.UNKNOWN

    def __str__(self) -> str:
        return f"Identity: nickname={self.nickname}, type={self.type}" + (
            f" username={self.username}, realname={self.realname}" if self.type == IdentityType.USER else ""
        )
