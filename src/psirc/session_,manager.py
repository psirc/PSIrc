import socket
import threading


class NickAlreadyInUse(Exception):
    pass


class NoSuchNick(Exception):
    pass


class SessionManager:
    """
    Manages the sockets connected to current server, including clients and server.
    """
    def __init__(self) -> None:
        self._clients: dict[str, socket.socket] = {}
        self._servers: dict[str, socket.socket] = {}
        self._clients_lock = threading.Lock()
        self._servers_lock = threading.Lock()

    def add_client(
            self, client_name: str, client_socket: socket.socket) -> None:
        """
        Add client to the list of locally connected clients

        :param client_name: name of client
        :type client_name: ``str``
        :param client_socket: socket object representing client connection
        :type client_socket: ``socket.socket``
        :raises NickAlreadyInUse: if client name is already in use
        :return: None
        :rtype: None
        """
        with self._clients_lock:
            if client_name in self._clients:
                raise NickAlreadyInUse(f"Nick \"{client_name}\" in use")
            
            external_server = self._external_clients.get(client_name)
            if external_server:
                raise NickAlreadyInUse(
                    f"Nick \"{client_name}\" in use on server {external_server}"
                )
            self._clients[client_name] = client_socket

    def add_server(
            self, server_name: str, server_socket: socket.socket) -> None:
        """
        Add server to the list of locally connected servers

        :param server_name: name of server
        :type server_name: ``str``
        :param server_socket: socket object representing server connection
        :type server_socket: ``socket.socket``
        :raises NickAlreadyInUse: if client name is already in use
        :return: None
        :rtype: None
        """
        with self._servers_lock:
            if server_name in self._servers:
                raise NickAlreadyInUse(f"Server name \"{server_name}\" in use")
            self._servers[server_name] = server_socket

    def get_client_socket(self, client_name: str) -> socket.socket | None:
        """
        Retrieve socket object for a locally connected client.

        :param client_name: name of the client
        :type client_name: ``str``
        :return: client's socket if found, otherwise None
        :rtype: ``socket.socket`` or ``None``
        """
        with self._clients_lock:
            return self._clients.get(client_name)

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

    def list_clients(self) -> list[str]:
        """
        List all locally connected clients

        :return: list of locally connected clients
        :rtype: ``list[str]``
        """
        with self._clients_lock:
            return list(self._clients.keys())

    def list_servers(self) -> list[str]:
        """
        List all locally connected servers

        :return: list of locally connected servers
        :rtype: ``list[str]``
        """
        with self._servers_lock:
            return list(self._servers.keys())

    def disconnect_client(self, client_name: str) -> None:
        """
        Close connection of locally connected client

        :param client_name: name of client
        :type client_name: ``str``
        :raises NoSuchNick: if client is not locally connected
        :return: None
        :rtype: None
        """
        with self._clients_lock:
            client_socket = self._clients.pop(client_name, None)

        if client_socket is None:
            raise NoSuchNick(
                f"Client \"{client_name}\" not connected to this server."
            )
        client_socket.close()

    def disconnect_server(self, server_name: str) -> None:
        """
        Close connection of locally connected server

        :param server_name: name of client
        :type server_name: ``str``
        :raises NoSuchNick: if server is not locally connected
        :return: None
        :rtype: None
        """
        with self._servers_lock:
            server_socket = self._servers.pop(server_name, None)

        if server_socket is None:
            raise NoSuchNick(
                f"Server \"{server_name}\" not connected to this server."
            )
        server_socket.close()
