import socket
import threading


class NickAlreadyInUse(Exception):
    pass


class NoSuchNick(Exception):
    pass


class SessionManager:
    """
    Manages the sockets connected to current server, including user and server.
    """
    def __init__(self) -> None:
        self._users: dict[str, socket.socket] = {}
        self._servers: dict[str, socket.socket] = {}
        self._users_lock = threading.Lock()
        self._servers_lock = threading.Lock()

    def add_user(
            self, user_nick: str, user_socket: socket.socket) -> None:
        """
        Add user to the list of locally connected users

        :param user_nick: nick of user
        :type user_nick: ``str``
        :param user_socket: socket object representing user connection
        :type user_socket: ``socket.socket``
        :raises NickAlreadyInUse: if user nick is already in use
        :return: None
        :rtype: None
        """
        with self._users_lock:
            if user_nick in self._users:
                raise NickAlreadyInUse(f"Nick \"{user_nick}\" in use")
            self._users[user_nick] = user_socket

    def add_server(
            self, server_name: str, server_socket: socket.socket) -> None:
        """
        Add server to the list of locally connected servers

        :param server_name: name of server
        :type server_name: ``str``
        :param server_socket: socket object representing server connection
        :type server_socket: ``socket.socket``
        :raises NickAlreadyInUse: if server name is already in use
        :return: None
        :rtype: None
        """
        with self._servers_lock:
            if server_name in self._servers:
                raise NickAlreadyInUse(f"Server name \"{server_name}\" in use")
            self._servers[server_name] = server_socket

    def get_user_socket(self, user_nick: str) -> socket.socket | None:
        """
        Retrieve socket object for a locally connected user.

        :param user_nick: name of the user
        :type user_nick: ``str``
        :return: users's socket if found, otherwise None
        :rtype: ``socket.socket`` or ``None``
        """
        with self._users_lock:
            return self._users.get(user_nick)

    def get_server_socket(self, server_name: str) -> socket.socket | None:
        """
        Retrieve socket object for a locally connected server.

        :param server_name: name of the server
        :type server_name: ``str``
        :return: server's socket if found, otherwise None
        :rtype: ``socket.socket`` or ``None``
        """
        with self._servers_lock:
            return self._servers.get(server_name)

    def list_users(self) -> list[str]:
        """
        List all locally connected users

        :return: list of locally connected users
        :rtype: ``list[str]``
        """
        with self._servers_lock:
            return list(self._users.keys())

    def list_servers(self) -> list[str]:
        """
        List all locally connected servers

        :return: list of locally connected servers
        :rtype: ``list[str]``
        """
        with self._servers_lock:
            return list(self._servers.keys())

    def remove_user(self, user_nick: str) -> None:
        """
        Remove user socket from 

        :param client_name: name of client
        :type client_name: ``str``
        :return: None
        :rtype: None
        """
        with self._users_lock:
            self._users.pop(user_nick, None)

    def remove_server(self, server_name: str) -> None:
        """
        Close connection of locally connected server

        :param server_name: name of client
        :type server_name: ``str``
        :raises NoSuchNick: if server is not locally connected
        :return: None
        :rtype: None
        """
        with self._servers_lock:
            self._servers.pop(server_name, None)
