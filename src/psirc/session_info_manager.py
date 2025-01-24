from psirc.session_info import SessionInfo, SessionType
import socket
import threading


class SessionInfoManager:
    def __init__(self) -> None:
        self._socket_info: dict[socket.socket, SessionInfo] = {}
        self._lock = threading.Lock()

    def add(self, client_socket: socket.socket, password: str | None) -> None:
        self._socket_info[client_socket] = SessionInfo(password)

    def get_info(self, client_socket: socket.socket) -> SessionInfo | None:
        with self._lock:
            return self._socket_info.get(client_socket)

    def remove(self, client_socket: socket.socket) -> None:
        self._socket_info.pop(client_socket, None)

    def get_sessions_by_type(self, type: SessionType) -> dict[socket.socket, SessionInfo]:
        result = {}
        with self._lock:
            for session in self._socket_info:
                if self._socket_info[session].type == type:
                    result[session] = self._socket_info[session]
        return result

    def get_socket(self, nickname: str) -> socket.socket | None:
        for sock, info in self._socket_info.items():
            if info.nickname == nickname:
                return sock
        return None
