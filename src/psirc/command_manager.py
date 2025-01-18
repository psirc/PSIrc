import socket
import logging
from typing import TypedDict
from typing_extensions import Unpack

from psirc.connection_manager import ConnectionManager
from psirc.message_parser import MessageParser
from psirc.message import Message, Prefix, Params
from psirc.defines.responses import Command
from psirc.identity_manager import IdentityManager
from psirc.identity import IdentityType, Identity
from psirc.session_manager import SessionManager
from psirc.response_params import parametrize
from psirc.routing_manager import RoutingManager
from psirc.channel_manager import ChannelManager
from psirc.password_handler import PasswordHandler
from psirc.irc_validator import IRCValidator
from psirc.defines.exceptions import NoSuchChannel


class CmdArgs(TypedDict):
    identity_manager: IdentityManager
    session_manager: SessionManager
    client_socket: socket.socket
    identity: None | Identity
    message: Message
    nickname: str
    connection_manager: ConnectionManager
    password_handler: PasswordHandler
    channel_manager: ChannelManager


def _quit_connection(**kwargs: Unpack[CmdArgs]) -> bool:
    message = kwargs["message"]
    client_socket = kwargs["client_socket"]
    identity = kwargs["identity"]
    session_manager = kwargs["session_manager"]
    identity_manager = kwargs["identity_manager"]
    connection_manager = kwargs["connection_manager"]

    if message.command is not Command.QUIT:
        return False
    connection_manager.disconnect_client(client_socket)
    if identity is None:
        return True
    identity_manager.remove(client_socket)
    if identity.type is IdentityType.USER:
        session_manager.remove_user(identity.nickname)
        # TODO : notify remote servers
    elif identity.type is IdentityType.SERVER:
        # TODO : server removal functionality
        pass
    return True


def try_handle_quit_command(**kwargs: Unpack[CmdArgs]) -> bool:
    '''Try to handle QUIT command.

    Command: QUIT
    Parameters: [<quit_message>]

    A client session is ended with a quit message.  The server must close
    the connection to a client which sends a QUIT message. If a "Quit
    Message" is given, this will be sent instead of the default message,
    the nickname.

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
    message = kwargs["message"]

    if message.command is not Command.QUIT:
        return False
    _quit_connection(**kwargs)
    return True


def try_handle_pass_command(**kwargs: Unpack[CmdArgs]) -> bool:
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

    message = kwargs["message"]
    identity = kwargs["identity"]
    client_socket = kwargs["client_socket"]
    identity_manager = kwargs["identity_manager"]

    if message.command is not Command.PASS:
        return False
    if identity is not None:
        # already registered
        # TODO : respond with already registered error
        pass
    else:
        # TODO: check for password -> password is checked later - now just connect it to identity
        logging.info("Set PASS")
        if message.params:
            identity_manager.add(client_socket, message.params["password"])
        # OK, no response to client
    return True


def try_handle_nick_command(**kwargs: Unpack[CmdArgs]) -> bool:
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

    message = kwargs["message"]
    identity = kwargs["identity"]
    client_socket = kwargs["client_socket"]
    identity_manager = kwargs["identity_manager"]

    if not identity:
        print("client connecting without pass, adding identity")
        identity_manager.add(client_socket, '')
        identity = identity_manager.get_identity(client_socket)

    if message.command is not Command.NICK:
        return False
    # TODO : check for nick collisions
    if message.params:
        identity.nickname = message.params["nickname"]
    # QUESTION : Do we want to handle nick change functionality
    return True


def try_handle_user_command(**kwargs: Unpack[CmdArgs]) -> bool:
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

    message = kwargs["message"]
    identity = kwargs["identity"]
    client_socket = kwargs["client_socket"]
    session_manager = kwargs["session_manager"]
    password_handler = kwargs["password_handler"]

    if not identity:
        return False

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
        if message.params:
            identity.username = message.params["username"]
            identity.realname = message.params["realname"]
            address = f"{message.params['hostname']}@{message.params['servername']}"
        else:
            return False

        if not password_handler.valid_password(address, identity.password):
            logging.info(f"Incorrect password given for {identity.username}")
            # TODO: Add ERR_PASSWDMISMATCH here
            _quit_connection(**kwargs)
            return False
        session_manager.add_user(identity.nickname, client_socket)
        logging.info(f"Registered: {identity}")

        response = Message(
            prefix=None,
            command=Command.RPL_WELCOME,
            params=parametrize(Command.RPL_WELCOME, nickname=identity.nickname),
        )
        print(f"welcome packet: [{str(response)}]")
        RoutingManager.respond_client(client_socket, response)
        # now that the three commands needed for registrations are present
        # server can verify user, and register user /
        # TODO: check user
    return True


def try_handle_server_command(**kwargs: Unpack[CmdArgs]) -> bool:
    message = kwargs["message"]
    identity = kwargs["identity"]

    if message.command is not Command.SERVER:
        return False
    # TODO : handle server registration
    if not identity:
        return False
    return True


def try_handle_privmsg_command(**kwargs: Unpack[CmdArgs]) -> bool:
    message = kwargs["message"]
    identity = kwargs["identity"]
    nickname = kwargs["nickname"]
    session_manager = kwargs["session_manager"]
    channel_manager: ChannelManager = kwargs["channel_manager"]
    client_socket = kwargs["client_socket"]

    if message.command is not Command.PRIVMSG:
        return False

    if not identity or not identity.registered():
        return False

    message.prefix = Prefix(identity.nickname, identity.username, nickname)

    receiver = None
    if message.params:
        receiver = message.params["receiver"]

    if not receiver:
        message_error = Message(
            prefix=None,
            command=Command.ERR_NONICKNAMEGIVEN,
            params=parametrize(Command.ERR_NONICKNAMEGIVEN),
        )
        RoutingManager.respond_client(client_socket, message_error)
        return False

    message_to_send = message

    try:
        if IRCValidator.validate_channel(receiver):
            channel_manager.forward_message(session_manager, identity.nickname, receiver, message_to_send)
        else:
            RoutingManager.send_to_user(receiver, message_to_send, session_manager)
    except NoSuchChannel:
        pass
        # TODO
        # message_error = Message(prefix=None, command=Command.ERR_NOSUCHCHANNEL, params=)
    except KeyError:
        message_error = Message(
            prefix=None,
            command=Command.ERR_NOSUCHNICK,
            params=parametrize(Command.ERR_NOSUCHNICK, nickname=receiver),
        )
        RoutingManager.respond_client(client_socket, message_error)


def try_handle_ping_command(**kwargs: Unpack[CmdArgs]) -> bool:
    identity = kwargs["identity"]
    message = kwargs["message"]
    client_socket = kwargs["client_socket"]

    if not identity or not identity.registered():
        return False

    receiver = message.params["receiver"] if message.params else ""  # this is us

    response = Message(prefix=None, command=Command.PONG, params=parametrize(Command.PONG, receivedby=receiver))
    client_socket.send(str(response).encode())
    return True


def try_handle_join_command(**kwargs: Unpack[CmdArgs]) -> bool:
    identity = kwargs["identity"]
    message = kwargs["message"]
    session_manager = kwargs["session_manager"]
    channel_manager = kwargs["channel_manager"]
    channel_name = message.params["channel"]

    # TODO handling banned users, and key protected channels + handle channel topic
    channel_manager.join(channel_name, identity.nickname)
    topic_rpl = Message(
        prefix=None,
        command=Command.RPL_TOPIC,
        params=parametrize(Command.RPL_TOPIC, channel=channel_name, trailing="No topic yet"),
    )
    print(topic_rpl)

    # handle better namereply
    names = channel_manager.get_names(channel_name)

    nam_rpl = Message(
        prefix=None,
        command=Command.RPL_NAMREPLY,
        params=parametrize(Command.RPL_TOPIC, channel=channel_name, trailing=names),
    )
    print(nam_rpl)

    RoutingManager.send_to_user(identity.nickname, topic_rpl, session_manager)
    RoutingManager.send_to_user(identity.nickname, nam_rpl, session_manager)


CMD_FUNCTIONS = {
    Command.PASS: try_handle_pass_command,
    Command.NICK: try_handle_nick_command,
    Command.USER: try_handle_user_command,
    Command.SERVER: try_handle_server_command,
    Command.PRIVMSG: try_handle_privmsg_command,
    Command.QUIT: try_handle_quit_command,
    Command.PING: try_handle_ping_command,
    Command.JOIN: try_handle_join_command,
}
