from concurrent.futures import ThreadPoolExecutor
import socket
from psirc.connection_manager import ConnectionManager
from psirc.message_parser import MessageParser
from psirc.message import Message, Params
from psirc.defines.responses import Command
from psirc.session_info import SessionInfo, SessionType
from psirc.session_info_manager import SessionInfoManager
from psirc.user_manager import UserManager
import psirc.command_manager as cmd_manager
from psirc.password_handler import PasswordHandler
from psirc.channel_manager import ChannelManager

import logging


class IRCServer:
    def __init__(
        self, nickname: str, host: str, port: int, max_workers: int = 10, *, password_file: str = "psirc.conf"
    ) -> None:
        self.running = False
        self.nickname = nickname
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)
        self._users = UserManager()
        self._sessions = SessionInfoManager()
        self._password_handler = PasswordHandler(password_file)
        self._channels = ChannelManager()

    def start(self) -> None:
        self.running = True
        self._connection.start()
        self._password_handler.parse_config()

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

                cmd_args = {
                    "identity_manager": self._identities,
                    "session_manager": self._sockets,
                    "client_socket": client_socket,
                    "identity": session_info,
                    "message": message,
                    "nickname": self.nickname,
                    "connection_manager": self._connection,
                    "password_handler": self._password_handler,
                    "channel_manager": self._channels,
                }

                if message.command not in cmd_manager.CMD_FUNCTIONS.keys():
                    continue
                try:
                    cmd_manager.CMD_FUNCTIONS[message.command](**cmd_args)
                except KeyError:
                    logging.warning(f"Unrecognized command: {message.command}.")
        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            logging.error(f"Aborting! Unhandled error:\n{e}")
        finally:
            self._connection.stop()
