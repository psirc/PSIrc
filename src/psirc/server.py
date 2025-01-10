import socket
from concurrent.futures import ThreadPoolExecutor
from psirc.connection_manager import ConnectionManager
from psirc.message_parser import MessageParser
from psirc.message import Message, Prefix
from psirc.defines.responses import Command
from psirc.identity_manager import IdentityManager
from psirc.identity import IdentityType, Identity
from psirc.session_manager import SessionManager
from psirc.response_params import parametrize

import logging


class IRCServer:
    def __init__(self, nickname: str, host: str, port: int, max_workers: int = 10) -> None:
        self.running = False
        self.nickname = nickname
        self._thread_executor = ThreadPoolExecutor(max_workers)
        self._connection = ConnectionManager(host, port, self._thread_executor)
        self._sockets = SessionManager()
        self._identities = IdentityManager()

    def start(self) -> None:
        self.running = True
        self._connection.start()

        while self.running:
            result = self._connection.get_message()
            if result is None:
                continue

            client_socket, data = result
            message = MessageParser.parse_message(data)
            if not message:
                logging.warning("Invalid message from client")
                # no response
                continue
            identity = self._identities.get_identity(client_socket)

            if not identity:
                # client not registered accept only PASS command
                if message.command is Command.PASS:
                    # TODO: check for password -> password is checked later - now just connect it to identity
                    logging.info("Set PASS")
                    self._identities.add(client_socket, message.params["password"])
                    # OK, no response to client
                else:
                    logging.warning("First command in registration process should be PASS")
                    # TODO : respond with not registered error
                continue

            if not identity.registered():
                # client has not set NICK and (USER or SERVER)
                if message.command is Command.NICK:
                    identity.nickname = message.params["nickname"]
                elif message.command is Command.USER and identity.nickname:
                    # TODO : parse nick command
                    identity.type = IdentityType.USER
                    identity.username = message.params["username"]
                    identity.realname = message.params["realname"]
                    self._sockets.add_user(identity.nickname, client_socket)
                    logging.info(f"Registered: {identity}")
                    # now that the three commands needed for registrations are present
                    # server can verify user, and register user /
                    # TODO: check user
                # TODO : add for elif Command.server similar to command user
                elif message.command is Command.PASS:
                    # TODO : respond with already registered error
                    pass
                else:
                    logging.warning("Client was not registered")
                    # TODO : respond with not registered error
                continue

            # client is registered and can send other commands
            if message.command is Command.PRIVMSG:
                self.handle_privmsg_command(client_socket, identity, message)
            elif message.command is Command.JOIN:
                self.handle_join_command(client_socket, identity, message)
            else:
                # TODO : respond with unknown command error
                pass

    def handle_privmsg_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> None:
        message.prefix = Prefix(identity.nickname, identity.username, self.nickname)
        receiver = message.params["receiver"]
        message_to_send = message

        if receiver in self._sockets._users.keys():
            logging.info(f"Forwarding private message: {message}")
            receiver_socket = self._sockets._users[receiver]
            receiver_socket.send(str(message_to_send).encode())
            return

        if not receiver:
            message_to_send = Message(
                prefix=None,
                command=Command.ERR_NONICKNAMEGIVEN,
                params=parametrize(Command.ERR_NONICKNAMEGIVEN),
            )
        else:
            message_to_send = Message(
                prefix=None,
                command=Command.ERR_NOSUCHNICK,
                params=parametrize(Command.ERR_NOSUCHNICK, nickname=receiver),
            )
        logging.warning(f"Sending ERR: {message}")
        client_socket.send(str(message_to_send).encode())

    def handle_join_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> None:
        pass
