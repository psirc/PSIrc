from enum import Enum, auto


class SessionType(Enum):
    UNKNOWN = 0
    USER = auto()
    SERVER = auto()
    EXTERNAL_USER = auto()

    def __str__(self) -> str:
        return self.name


class SessionInfo:
    """Represents user or server.
    attributes:

        :param type: server or user
        :type type: ``SessionType``
        :param nickname: nick of user or server
        :type nickname: ``str``
        :param password: set password, which will be used to register user
        :type password: ``str``
        :param username: username
        :type username: ``str``
        :param realname: real name of user - contains space
        :type realname: ``str``
    """

    def __init__(self, password: str | None) -> None:
        self.password = password
        self.nickname = ""
        self.username = ""
        self.realname = ""
        self.hops = 0
        self.type = SessionType.UNKNOWN

    def registered(self) -> bool:
        """Checks if session has marks indicating registered status.

        :return: is session registered
        :rtype: ``bool``
        """
        return bool(self.nickname and self.type is not SessionType.UNKNOWN)

    def __str__(self) -> str:
        return f"Identity: nickname={self.nickname}, type={self.type}" + (
            f" username={self.username}, realname={self.realname}" if self.type == SessionType.USER else ""
        )
