import socket
import threading
from psirc.defines.exceptions import NoSuchNick, NickAlreadyInUse
from psirc.client import Client, LocalUser, ExternalUser, Server
from collections.abc import Sequence


class ClientManager:
    """
    Manages the sockets connected to current server, including user and server.
    """

    def __init__(self) -> None:
        self._users: dict[str, LocalUser | ExternalUser] = dict()
        self._servers: dict[str, Server] = dict()
        self._lock = threading.Lock()

    def add_local(self, user_nick: str, user_socket: socket.socket) -> None:
        """
        Add local user to the list of users

        :param user_nick: nick of user
        :type user_nick: ``str``
        :param user_socket: socket object representing user connection
        :type user_socket: ``socket.socket``
        :raises NickAlreadyInUse: if user nick is already in use
        :return: None
        :rtype: None
        """
        with self._lock:
            if user_nick in self._users.keys():
                raise NickAlreadyInUse(f'Nick "{user_nick}" in use')
            self._users[user_nick] = LocalUser(user_nick, user_socket)

    def add_external(self, user_nick: str, hop_count: int, server_name: str) -> None:
        """
        Add external user to the list of users

        :param user_nick: nick of user
        :type user_nick: ``str``
        :param hop_count: distance from server
        :type hop_count: ``int``
        :raises NickAlreadyInUse: if user nick is already in use
        :return: None
        :rtype: None
        """
        if hop_count < 1:
            raise ValueError(f'Hop count of external user "{user_nick}" has to be a positive int')
        with self._lock:
            if user_nick in self._users.keys():
                raise NickAlreadyInUse(f'Nick "{user_nick}" in use')
            self._users[user_nick] = ExternalUser(user_nick, hop_count, server_name)

    def add_server(self, server_nick: str, hop_count: int) -> None:
        if hop_count < 1:
            raise ValueError("Hop count of server has to be a positive integer")
        with self._lock:
            if server_nick in self._servers.keys():
                raise NickAlreadyInUse(f"Nickname '{server_nick}' is already in use!")
            self._servers[server_nick] = Server(server_nick, hop_count)

    def get_user(self, user_nick: str) -> Client | None:
        """
        Retrieve User object for a user.

        :param user_nick: name of the user
        :type user_nick: ``str``
        :return: User object if found, otherwise None
        :rtype: ``User`` or ``None``
        """
        with self._lock:
            return self._users.get(user_nick)

    def get_server(self, server_nick: str) -> Server | None:
        with self._lock:
            return self._servers.get(server_nick)

    def list_users(self) -> list[str]:
        """
        List all users

        :return: list of users
        :rtype: ``list[str]``
        """
        with self._lock:
            return list(self._users.keys())

    def remove(self, user_nick: str) -> None:
        """
        Remove local or external user

        :param client_name: name of client
        :type client_name: ``str``
        :return: None
        :rtype: None
        """
        with self._lock:
            self._users.pop(user_nick, None)

    def remove_from_server(self, server_nickname: str) -> Sequence[Client]:  # Sequence is used for derived client types
        """
        Remove all users socket from

        :param client_name: name of client
        :type client_name: ``str``
        :return: list of removed users
        :rtype: a Sequence object of users
        """
        with self._lock:
            disconnected_users = [
                user
                for user in self._users.values()
                if isinstance(user, ExternalUser) and user.location == server_nickname
            ]
            for user in disconnected_users:
                self._users.pop(user.nick)
            return disconnected_users

    def add_oper_privileges(self, user_nick: str) -> None:
        with self._lock:
            if user_nick not in self._users.keys():
                raise NoSuchNick()

            user = self._users[user_nick]
            if isinstance(user, LocalUser):
                user.is_oper = True

    def has_oper_privileges(self, user_nick: str) -> bool:
        with self._lock:
            if user_nick in self._users.keys() and isinstance((user := self._users[user_nick]), LocalUser):
                return user.is_oper
            return False

    def get_local_users(self) -> list[str]:
        result = []
        with self._lock:
            for user in self._users:
                if isinstance(self._users[user], LocalUser):
                    result.append(user)
        return result
    
    def list_servers(self) -> dict[str, Server]:
        with self._lock:
            return self._servers
