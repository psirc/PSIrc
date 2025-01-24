from psirc.session_info import SessionInfo, SessionType
import socket
import threading


class SessionInfoManager:
    """Holds SessionInfo associated with socket

    :field _socket_info: socket to SessionInfo association
    :type nickname: ``dict[socket.socket, SessionInfo]``
    """
    def __init__(self) -> None:
        self._socket_info: dict[socket.socket, SessionInfo] = {}

    def add(self, client_socket: socket.socket, password: str | None) -> None:
        """Create new SessionInfo to SessionManager
        
        :param client_socket: socket of some local client
        :type client_socket: ``socket.socket``
        :param password: optional, password with which session will be registered
        :type password: ``str``
        """
        self._socket_info[client_socket] = SessionInfo(password)

    def get_info(self, client_socket: socket.socket) -> SessionInfo | None:
        """Retrieve sessionInfo associated with socket
        
        :param client_socket: socket of some local client
        :type client_socket: ``socket.socket``
        :return: SessionInfo associated with socket, None if socket was not yet added
        :rtype: ``SessionInfo | None``
        """
        return self._socket_info.get(client_socket)

    def remove(self, client_socket: socket.socket) -> None:
        """Remove sessionInfo associated with socket
        
        :param client_socket: socket of some local client
        :type client_socket: ``socket.socket``
        """
        self._socket_info.pop(client_socket, None)

    def get_sessions_by_type(self, type: SessionType) -> dict[socket.socket, SessionInfo]:
        """Return all sessionInfo of one type
        
        :param type: type of SessionInfo
        :type type: ``SessionType``
        :return: dictionary of socket to SessionInfo associations where only SessionInfo of type is present
        :rtype: ``dict[socket.socket, SessionInfo]``
        """
        result = {}
        for session in self._socket_info:
            if self._socket_info[session].type == type:
                result[session] = self._socket_info[session]
        return result

    def get_socket(self, nickname: str) -> socket.socket | None:
        """Return socket associated with a nickname
        
        :param nickname: nickname
        :type type: ``str``
        :return: socket associated with nickname, not if no association exists
        :rtype: ``socket.socket | None``
        """
        for sock, info in self._socket_info.items():
            if info.nickname == nickname:
                return sock
        return None
