import socket
from concurrent.futures import ThreadPoolExecutor
from connection_manager import ConnectionManager
from message_parser import MessageParser
from message import Message
from defines.commands import IRCCommand
from identity_manager import IdentityManager
from identity import IdentityType, Identity
from session_manager import SessionManager

import logging


class IRCServer:
    def __init__(
            self,
            nick: str, host: str, port: int,
            max_workers: int = 10
    ) -> None:
        self.running = False
        self.nick = nick
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)
        self._sockets = SessionManager()
        self._identities = IdentityManager()

    def start(self) -> None:
        self.running = True
        self._connection.start()

        while self.running:
            client_socket, data = self._connection.get_message()
            message = MessageParser.parse_message(data)
            if not message:
                logging.warning("Invalid message from client")
                # no response
                continue
            identity = self._identities.get_identity(client_socket)

            if not identity:
                # client not registered accept only PASS command
                if message.command is IRCCommand.PASS:
                    # TODO: check for password
                    logging.info("New client registered")
                    self._identities.add(client_socket)
                    # OK, no response to client
                else:
                    logging.warning("Client was not registered")
                    # TODO : respond with not registered error
                continue
            
            if not identity.registered():
                # client has not set NICK and (USER or SERVER)
                if message.command is IRCCommand.NICK:
                    # TODO : check for nick collisions
                    identity.nick = message.params.params
                elif message.command is IRCCommand.USER and identity.nick:
                    # TODO : parse nick command
                    identity.type = IdentityType.USER
                    self._sockets.add_user(identity.nick, client_socket)
                # TODO : add for elif irccommand.server similar to command user
                else:
                    logging.warning("Client was not registered")
                    # TODO : respond with not registered error
                continue
            # client is registered and can send commands

            if message.command is IRCCommand.PRIVMSG:
                self.handle_privmsg_command(client_socket, identity, message)
            elif message.command is IRCCommand.JOIN:
                self.handle_join_command(client_socket, identity, message)
            else:
                # TODO : respond with unknown command error
                pass

    def handle_privmsg_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> None:
        pass

    def handle_join_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> None:
        pass
