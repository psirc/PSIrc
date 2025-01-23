import socket


class Client:
    """
    Class representing a base client (user or server)

    :param nick: the nickname of client
    :type nick: ``str``
    """

    def __init__(self, nick: str) -> None:
        self._nick = nick

    @property
    def nick(self) -> str:
        return self._nick


class LocalUser(Client):
    """
    Class representing a local server user

    :param nick: the nickname of the user
    :type nick: ``str``
    :param socket: the socket at which the user is located
    :type socket: ``socket.socket``
    """

    def __init__(self, nick: str, socket: socket.socket) -> None:
        super().__init__(nick)
        self._socket = socket

    @property
    def socket(self) -> socket.socket:
        return self._socket


# TODO: Possibly change location and hop_count into a list with each hop (or even just next hop?)
class ExternalUser(Client):
    """
    Class representing a local server user

    :param nick: the nickname of the user
    :type nick: ``str``
    :param hop_count: the number of hops required to reach the server
    :type hop_count: int
    :param location: the server at which the user is located
    :type location: ``str``
    """

    def __init__(self, nick: str, hop_count: int, location: str) -> None:
        super().__init__(nick)
        self._location = location
        self._hop_count = hop_count

    @property
    def location(self) -> str:
        return self._location

    @property
    def hop_count(self) -> int:
        return self._hop_count


class Server(Client):
    def __init__(self, nick: str, hop_count: int) -> None:
        super().__init__(nick)
        self._hop_count = hop_count

    @property
    def hop_count(self) -> int:
        return self._hop_count
