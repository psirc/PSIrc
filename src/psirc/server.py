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
            if self.try_handle_privmsg_command(client_socket, identity, message):
                continue
            elif self.try_handle_join_command(client_socket, identity, message):
                continue

            # TODO : respond with unknown command error
            


    def try_handle_pass_command(
            self,
            client_socket: socket.socket,
            identity: None | Identity,
            message: Message
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
        if message.command is not IRCCommand.PASS:
            return False
        if identity is not None:
            # already registered
            # TODO : respond with already registered error
            pass
        else:
            # TODO: check for password
            logging.info("New client registered")
            self._identities.add(client_socket)
            # OK, no response to client
        return True

    def try_handle_nick_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> bool:
        '''Try to handle NICK command.

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
        '''
        if message.command is not IRCCommand.NICK:
            return False
        # TODO : check for nick collisions
        identity.nick = message.params
        # QUESTION : Do we want to handle nick change functionality
        return True

    def try_handle_user_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> None:
        '''Try Handle USER command.

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
        '''
        if message.command is not IRCCommand.USER:
            return False
        if identity.registered():
            if identity.type is IdentityType.SERVER:
                # Other server indicates new remote user arrival
                # TODO : handle new user registration from server
                pass
            else:
                # Local user already registered
                # TODO : respond with already registered error
                pass
        elif not identity.nick:
            # User must first set nick with NICK command
            # TODO : respond with error not registered
            pass
        else:
            # TODO : parse user command
            identity.type = IdentityType.USER
            self._sockets.add_user(identity.nick, client_socket)
        return True

    def try_handle_server_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> bool:
        if message.command is not IRCCommand.SERVER:
            return False
        # TODO : handle server registration
        return True

    def try_handle_privmsg_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> None:
        if message.command is not IRCCommand.PRIVMSG:
            return False
        # TODO : implement private messaging
        return True

    def try_handle_join_command(
            self,
            client_socket: socket.socket,
            identity: Identity,
            message: Message
    ) -> None:
        if message.command is not IRCCommand.JOIN:
            return False
        # TODO : implement joining rooms
        return True
