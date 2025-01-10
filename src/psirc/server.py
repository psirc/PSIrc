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
                # server sends no response
                continue
            identity = self._identities.get_identity(client_socket)
            message_params = (client_socket, identity, message)

            if self.try_handle_pass_command(*message_params):
                continue
            if not identity:
                # None identity: client has not successfully send PASS command
                # TODO : respond with error not registered
                continue

            if self.try_handle_nick_command(*message_params):
                continue
            elif self.try_handle_user_command(*message_params):
                continue
            elif self.try_handle_server_command(*message_params):
                continue

            if not identity.registered():
                # client didn't register NICK or didn't register as USER/SERVER
                # TODO : respond with not registered
                continue

            # client is registered
            if self.try_handle_privmsg_command(*message_params):
                continue
            elif self.try_handle_join_command(*message_params):
                continue

            # TODO : respond with unknown command error

    def try_handle_pass_command(
        self, client_socket: socket.socket, identity: None | Identity, message: Message
    ) -> bool:
        '''Try to handle PASS command.

        Command: PASS
        Parameters: <password>

        The password must be set before any attempt to register the connection
        is made, even if server is not password protected.

        Setting a password results in creation of Identity associated with
        socket in self._identities

        :param client_socket: Socket from which message was received
        :param type: ``socket``
        :param identity: Identity associated with socket
        :param type: ``Identity`` or ``None``
        :param message: Parsed message received from socket
        :param type: ``Message``
        :return: True if message command is PASS, False otherwise
        :rtype: ``bool``
        """
        '''
        if message.command is not Command.PASS:
            return False
        if identity is not None:
            # already registered
            # TODO : respond with already registered error
            pass
        else:
            # TODO: check for password -> password is checked later - now just connect it to identity
            logging.info("Set PASS")
            self._identities.add(client_socket, message.params["password"])
            # OK, no response to client
        return True

    def try_handle_nick_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> bool:
        """Try to handle NICK command.

        Command: NICK
        Parameters: <nickname> [ <hop_count> ]

        NICK message is used to give user or server a nickname. The <hop_count>
        parameter is only used by servers to indicate how far away a nick is
        from its home server.  A local connection has a hop_count of 0. If
        supplied by a client, it must be ignored.

        :param client_socket: Socket from which message was received
        :param type: ``socket``
        :param identity: Identity associated with socket
        :param type: ``Identity`` or ``None``
        :param message: Parsed message received from socket
        :param type: ``Message``
        :return: True if message command is NICK, False otherwise
        :rtype: ``bool``
        """
        if message.command is not Command.NICK:
            return False
        # TODO : check for nick collisions
        identity.nickname = message.params["nickname"]
        # QUESTION : Do we want to handle nick change functionality
        return True

    def try_handle_user_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> bool:
        """Try Handle USER command.

        Command: USER
        Parameters: <username> <hostname> <servername> <real_name>

        The USER message is used at the beginning of connection to specify
        the username, hostname, servername and realname of new user. It is
        also used in communication between servers to indicate new user
        arriving on IRC, since only after both USER and NICK have been
        received from a client does a user become registered.

        :param client_socket: Socket from which message was received
        :param type: ``socket``
        :param identity: Identity associated with socket
        :param type: ``Identity`` or ``None``
        :param message: Parsed message received from socket
        :param type: ``Message``
        :return: True if message command is NICK, False otherwise
        :rtype: ``bool``
        """
        if message.command is not Command.USER:
            return False
        if identity.registered():
            if identity.type is IdentityType.SERVER:
                # Other server indicates new remote user arrival
                # TODO : handle new user registration from server
                pass
            else:
                # Local user who is already registered
                # TODO : respond with already registered error
                pass
        elif not identity.nickname:
            # User must first set nick with NICK command
            # TODO : respond with error not registered
            pass
        else:
            identity.type = IdentityType.USER
            identity.username = message.params["username"]
            identity.realname = message.params["realname"]
            self._sockets.add_user(identity.nickname, client_socket)
            logging.info(f"Registered: {identity}")
            # now that the three commands needed for registrations are present
            # server can verify user, and register user /
            # TODO: check user
        return True

    def try_handle_server_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> bool:
        if message.command is not Command.SERVER:
            return False
        # TODO : handle server registration
        return True

    def try_handle_privmsg_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> bool:
        if message.command is not Command.PRIVMSG:
            return False

        message.prefix = Prefix(identity.nickname, identity.username, self.nickname)
        receiver = message.params["receiver"]
        message_to_send = message

        receiver_socket = self._sockets.get_user_socket(receiver)
        if receiver_socket:
            logging.info(f"Forwarding private message: {message}")
            receiver_socket.send(str(message_to_send).encode())
            return True

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
        return True

    def try_handle_join_command(self, client_socket: socket.socket, identity: Identity, message: Message) -> bool:
        if message.command is not Command.JOIN:
            return False
        # TODO : implement joining rooms
        return True
