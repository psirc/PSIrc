from identity import Identity
import socket


class IdentityManager:
    def __init__(self) -> None:
        self._socket_identity: dict[socket.socket, Identity] = {}

    def add(self, client_socket: socket.socket) -> None:
        self._socket_identity[client_socket] = Identity()

    def get_identity(self, client_socket: socket.socket) -> Identity | None:
        self._socket_identity.get(client_socket)

    def remove(self, client_socket: socket.socket) -> None:
        self._socket_identity.pop(client_socket, None)
