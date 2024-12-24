from dataclasses import dataclass, field


class Prefix:
    """
    Class representing a prefix for an IRC message
    attributes:
        sender - string, the sender of the message
    fields:
        user - string, recepient of the message (name)
        host - string, recepient of the message (host)
    """
    sender: str = ""

    def __init__(self, user: str = "", host: str = "") -> None:
        self._user = user
        self._host = host
        self._set_hostname()

    def _set_hostname(self) -> None:
        self._hostname = f"{self._user}{'@' if self._host else ''}{self._host}"

    def __str__(self) -> str:
        hostname = f"{self._user}{'@' if self._host else ''}{self._host}"
        return f":{getattr(self, "sender")}{'!' if hostname else ''}{hostname} "


# TODO: find a way to better represent params in code
class Params:
    def __init__(self, params: list | None = None) -> None:
        self.params = params if params else []

    def __str__(self) -> str:
        return " ".join(self.params)


@dataclass(kw_only=True)
class Message:
    prefix: Prefix | None = field()
    command: str = field()
    params: Params | None = field()

    def __str__(self) -> str:
        return f"{self.prefix}{self.command} {self.params}\r\n"
