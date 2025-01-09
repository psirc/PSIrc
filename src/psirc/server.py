from connection_manager import ConnectionManager
from concurrent.futures import ThreadPoolExecutor
from message import Message, Prefix
from message_parser import MessageParser
from identity_manager import IdentityManager
from defines.commands import IRCCommand
from defines.responses import Command

import logging


class IRCServer:
    def __init__(self, nick: str, host: str, port: int, max_workers: int = 10) -> None:
        self.running = False
        self.nick = nick
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)
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
                    client_socket.sendall(Message(prefix=Prefix(self.nick), command=Command(451)))
                    continue
                self._identities.add(client_socket)
                # 
