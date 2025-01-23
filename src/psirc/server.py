from concurrent.futures import ThreadPoolExecutor
import socket
import importlib
from psirc.connection_manager import ConnectionManager
from psirc.message_parser import MessageParser
from psirc.session_info import SessionInfo, SessionType
from psirc.session_info_manager import SessionInfoManager
from psirc.user_manager import UserManager
from psirc.password_handler import PasswordHandler
from psirc.channel_manager import ChannelManager

import logging


class AlreadyRegistered(Exception):
    pass


class IRCServer:
    def __init__(
        self, nickname: str, host: str, port: int, max_workers: int = 10, *, password_file: str = "psirc.conf"
    ) -> None:
        self.running = False
        self.nickname = nickname
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._password_handler = PasswordHandler(password_file)
        self._connection = ConnectionManager(host, port, self._thread_executor)
        self._sessions = SessionInfoManager()
        self._users = UserManager()
        self._channels = ChannelManager()
        self._commands = importlib.import_module("psirc.command_manager").CMD_FUNCTIONS

    def start(self) -> None:
        self._password_handler.parse_config()
        self.running = True
        self._connection.start()
        
        try:
            while self.running:
                result = self._connection.get_message(timeout=1)
                if result is None:
                    continue

                client_socket, data = result
                message = MessageParser.parse_message(data)
                if not message:
                    logging.warning(f"Invalid message from client:\n{data}")
                    # server sends no response
                    continue
                session_info = self._sessions.get_info(client_socket)

                if message.command not in self._commands.keys():
                    continue
                try:
                    command_handler = self._commands[message.command]
                except KeyError:
                    logging.warning(f"Unrecognized command: {message.command}.")
                command_handler(self, client_socket, session_info, message)
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            logging.error(f"Aborting! Unhandled error:\n{e}")
        finally:
            self._connection.stop()

    def remove_external_user(self, client_nick: str) -> None:
        """Remove external user from server.

        Remove user from list of users, channels.
        """
        self._users.remove(client_nick)
        self._channels.quit(client_nick)

    def remove_local_user(self, client_socket: socket.socket, session_info: SessionInfo | None) -> bool:
        """Remove local user from server.

        Remove user from list of users, channels. Disconnects the user from server
        """
        self._connection.disconnect_client(client_socket)
        if session_info is None:
            return True
        self._sessions.remove(client_socket)
        if session_info.type is not SessionType.USER:
            raise ValueError("Server need to quit using SQUIT command")
        self._users.remove(session_info.nickname)
        self._channels.quit(session_info.nickname)
        return True

    def register_local_connection(self, client_socket: socket.socket, session_info: SessionInfo | None, password: str | None) -> None:
        """Register local connection.
        """
        if session_info is not None:
            raise AlreadyRegistered("Client already registered")
        # password is checked later - now just add session_info
        self._sessions.add(client_socket, password if password else '')

    def is_unique(self, nickname: str) -> bool:
        if nickname == self.nickname:
            return False
        if nickname in self._users.list_users():
            return False
    
        return True

    def register_local_user(self, client_socket: socket.socket, session_info: SessionInfo) -> None:
        """Register local user.

        """
        self._users.add_local(session_info.nickname, client_socket)

    def register_server(self, session_info: SessionInfo) -> None:
        self._users.add_server(session_info.nickname, session_info.hops)

