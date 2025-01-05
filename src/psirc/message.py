from __future__ import annotations
from dataclasses import dataclass, field
from psirc.defines.responses import Command


class Prefix:
    """
    Class representing a prefix for an IRC message
    attributes:
        sender - string, the sender of the message
    fields:
        user - string, recepient of the message (name)
        host - string, recepient of the message (host)
    """

    def __init__(self, sender: str, user: str = "", host: str = "") -> None:
        self.sender = sender
        self.user = user
        self.host = host.lower()
        self._set_hostname()

    def _set_hostname(self) -> None:
        self._hostname = f"{self.user}{'@' if self.host else ''}{self.host}"

    def __str__(self) -> str:
        hostname = f"{self.user}{'@' if self.host else ''}{self.host}"
        return f":{self.sender}{'!' if hostname else ''}{hostname}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Prefix):
            return NotImplemented
        return all((self.sender == other.sender, self.user == other.user, self.host == other.host))


# TODO: find a way to better represent params in code
class Params:
    def __init__(self, params: dict | None = None) -> None:
        self.params = params if params else []

    def __str__(self) -> str:
        return " ".join(self.params)


@dataclass(kw_only=True)
class Message:
    prefix: Prefix | None = field()
    command: Command = field()
    params: Params | None = field()

    def __str__(self) -> str:
        return f"{self.prefix}{self.command} {self.params}\r\n"
