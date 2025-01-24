from __future__ import annotations
from dataclasses import dataclass, field
from psirc.defines.responses import Command


class Prefix:
    """
    Class representing a prefix for an IRC message

    :param sender: the sender of the message
    :type sender: `string`
    :field user: recepient of the message (name)
    :type user: `string`
    :field host: recepient of the message (host)
    :type host: `string`
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

    #def __eq__(self, other: object) -> bool:
    #    if not isinstance(other, Prefix):
    #        return NotImplemented
    #    return all(
    #        (
    #            self.sender == other.sender,
    #            self.user == other.user,
    #            self.host == other.host,
    #        )
    #    )


class Params:
    def __init__(self, params: dict[str, str] | None = None, *, recepient: str | None = None) -> None:
        self.params = params if params else {}
        self.recepient = recepient if recepient else ""  # used in numeric replies

    def __str__(self) -> str:
        return (self.recepient + " " if self.recepient else "") + " ".join(
            (":" if key == "trailing" else "") + self[key] for key in self.params.keys() if self[key]
        )

    def __getitem__(self, key: str) -> str:
        return self.params[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.params[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.params


@dataclass(kw_only=True)
class Message:
    prefix: Prefix | None = field()
    command: Command = field()
    params: Params | None = field()

    def __str__(self) -> str:

        return (" ".join((str(x) for x in (self.prefix, self.command, self.params) if x))).strip() + "\r\n"
