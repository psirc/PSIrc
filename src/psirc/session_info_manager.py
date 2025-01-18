from psirc.session_info import SessionInfo
import socket


class SessionInfoManager:
    def __init__(self) -> None:
        self._socket_info: dict[socket.socket, SessionInfo] = {}

    def add(self, client_socket: socket.socket, password: str) -> None:
        self._socket_info[client_socket] = SessionInfo(password)

    def get_info(self, client_socket: socket.socket) -> SessionInfo | None:
        return self._socket_info.get(client_socket)

    def remove(self, client_socket: socket.socket) -> None:
        self._socket_info.pop(client_socket, None)
