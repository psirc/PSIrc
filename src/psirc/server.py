from connection_manager import ConnectionManager
from concurrent.futures import ThreadPoolExecutor
from message_parser import MessageParser
from defines.commands import IRCCommand
from identity_manager import IdentityManager
from session_manager import SessionManager

import logging


class IRCServer:
    def __init__(self, nick: str, host: str, port: int, max_workers: int = 10) -> None:
        self.running = False
        self.nick = nick
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)
        self._sessions = SessionManager()
        self._identities = IdentityManager()

    def start(self) -> None:
        self.running = True
        self._connection.start()
        while self.running:
            client_socket, data = self._connection.get_message()
            message = MessageParser.parse_message(data)
            identity = self._identities.get_identity(client_socket)

            if not identity:
                # client not registered accept only PASS command
                if message.command is not IRCCommand.PASS:
                    logging.warning("Client was not registered")
                    # TODO : respond with not registered error
                    continue
                # TODO: check for password
                self._identities.add(client_socket)
                # OK, no response to client
                continue
            if not identity.registered():
                # client has not set NICK and/or USER
                pass
            # client is registered
            if message.command is IRCCommand.
