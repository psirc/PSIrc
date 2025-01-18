import socket


class User:
    """
    Class representing a user
    attributes:
        nick - string, the nickname of user
        hop_count - int, distance from server, local users have hop count 0
        route - socket or str, local user's socket or external users server nickname
    """
    def __init__(self, nick: str, hop_count: int, route: socket.socket | str) -> None:
        self._nick = nick
        self._hop_count = hop_count
        self._route = route

    @property
    def nick(self) -> str:
        return self._nick

    def is_local(self) -> bool:
        return self._hop_count == 0

    @property
    def hop_count(self) -> str:
        return self._hop_count

    def get_route(self) -> socket.socket | str:
        """Get socket of local user or external user's server nickname

        :return: local user socket or external user's server nickname
        :rtype: ``socket.socket`` or ``str``
        """
        return self._route
