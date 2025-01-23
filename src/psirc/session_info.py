from enum import Enum, auto


class SessionType(Enum):
    UNKNOWN = 0
    USER = auto()
    SERVER = auto()

    def __str__(self) -> str:
        return self.name


class SessionInfo:
    """Represents user or server.
    attributes:
        type - ``SessionType``, server or user
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
        self.is_oper = False
        self.type = SessionType.UNKNOWN

    def registered(self) -> bool:
        return bool(self.nickname and self.type is not SessionType.UNKNOWN)

    def __str__(self) -> str:
        return f"Identity: nickname={self.nickname}, type={self.type}" + (
            f" username={self.username}, realname={self.realname}" if self.type == SessionType.USER else ""
        )
