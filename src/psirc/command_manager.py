import socket
import logging

from psirc.server import IRCServer, AlreadyRegistered
from psirc.message import Message, Prefix
from psirc.defines.responses import Command
from psirc.session_info import SessionInfo, SessionType
from psirc.routing_manager import RoutingManager
from psirc.irc_validator import IRCValidator
from psirc.defines.exceptions import NoSuchChannel, NoSuchNick, NotOnChannel, ChanopPrivIsNeeded

import psirc.command_helpers as helpers


def handle_connect_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo, message: Message
) -> None:

    nickname = session_info.nickname
    if not server._users.has_oper_privileges(nickname):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NOPRIVILEGES, nickname if nickname else "*")
        return
    if not message.params or "target_server" not in message.params:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, session_info.nickname)
        return

    # remote server connecting
    if "remote_server" in message.params:
        # TODO: Connect a remote server to another remote server
        # Forward this message to server
        ...
        return

    target_server = message.params["target_server"]
    print(f"target server: {target_server}")
    port = message.params["port"] if message.params["port"] else str(server.port)
    print(f"port: {port}")

    # get server socket
    server_socket = server.connect_to_server(target_server, port)
    if not server_socket:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NOSUCHSERVER, session_info.nickname)
        return
    print(f"connected to server {target_server}:{port}")

    # create session
    server.register_local_connection(server_socket, None, None)
    server_session = server._sessions.get_info(client_socket)
    if not server_session:
        return

    # set password
    server_session.password = server.password_handler.get_c_password(target_server)
    if not server_session.password:
        print("Connected to server but no password found")
        # TODO: raise some error or log in console?
        return

    print(f"found password: {server_session.password}")
    print(f"server nickname: {server.nickname}")

    # Send PASS message
    RoutingManager.send_command(server_socket, command=Command.PASS, password=server_session.password)

    # Send SERVER message
    RoutingManager.send_command(
        server_socket,
        Prefix(server.nickname),
        command=Command.SERVER,
        servername=server.nickname,
        hopcount="1",
        trailing="Placeholder server message",
    )
    helpers.send_local_user_nicks(server_socket, server, "1")
    helpers.send_external_user_nicks(server_socket, server)


def handle_oper_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """Handle Oper command.

    Command: OPER
        Parameters: <user> <password>

    Numeric Replies:
    - ERR_NEEDMOREPARAMS
    - ERR_PASSWDMISMATCH
    - ERR_NOTREGISTERED
    - RPL_YOUROPER

    If the user is known (registered), tries to obtain irc operator privileges.
    Checks if required params are provided (user, password).
    If credentials are correct user is granted operator privileges and recieved RPL_YOUROPER

    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :return: None
    :rtype: None
    """
    if not session_info:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NOTREGISTERED, "*")
        return
    if message.command is not Command.OPER:
        raise ValueError("Implementation error: Wrong command type")
    # if session_info is not None and session_info.type is SessionType.USER
    if not message.params or ("user" not in message.params or "password" not in message.params):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, session_info.nickname)
        return

    if server.password_handler.valid_operator(message.params["user"], message.params["password"]):
        server._users.add_oper_privileges(session_info.nickname)
        RoutingManager.respond_client(client_socket, command=Command.RPL_YOUREOPER, recepient=session_info.nickname)
    else:
        RoutingManager.respond_client_error(client_socket, Command.ERR_PASSWDMISMATCH, session_info.nickname)


def handle_quit_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """Handle QUIT command.

    Description:
    Command: QUIT
    Parameters: [<quit_message>]

    A client session is ended with a quit message.  The server must close
    the connection to a client which sends a QUIT message. If a "Quit
    Message" is given, this will be sent instead of the default message,
    the nickname.

    :param client_socket: Socket from which message was received
    :type client_socket: ``socket``
    :param identity: Identity associated with socket
    :type identity: ``Identity`` or ``None``
    :param message: Parsed message received from socket
    :type message: ``Message``
    :return: None
    """

    if message.command is not Command.QUIT:
        raise ValueError("Implementation error: Wrong command type")
    if session_info is None or session_info.type is SessionType.USER:
        server.remove_local_user(client_socket, session_info)
    elif session_info.type is SessionType.SERVER and message.prefix:
        server.remove_external_user(message.prefix.user)
    else:
        raise ValueError("Unhandled quit command error")
    # TODO: notify other servers about user quit


def handle_pass_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """Try to handle PASS command.

    Command: PASS
    Parameters: <password>

    The password must be set before any attempt to register the connection
    is made, even if server is not password protected.

    Setting a password results in creation of Identity associated with
    socket in self._identities

    :param client_socket: Socket from which message was received
    :type client_socket: ``socket``
    :param identity: Identity associated with socket
    :type identity: ``Identity`` or ``None``
    :param message: Parsed message received from socket
    :type message: ``Message``
    :return: True if message command is PASS, False otherwise
    :rtype: ``bool``
    """

    if message.command is not Command.PASS:
        raise ValueError("Implementation error: Wrong command type")
    try:
        if message.params:
            server.register_local_connection(client_socket, session_info, message.params["password"])
        else:
            # missing params
            RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, "*")
            raise ValueError("Missing params from message command PASS")
        # OK, no response to client
    except AlreadyRegistered:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_ALREADYREGISTRED, session_info.nickname if session_info else "*"
        )
    # OK, no response to client


def handle_nick_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """Handle NICK command.

    Command: NICK
    Parameters: <nickname> [ <hop_count> ]

    NICK message is used to give user or server a nickname. The <hop_count>
    parameter is only used by servers to indicate how far away a nick is
    from its home server.  A local connection has a hop_count of 0. If
    supplied by a client, it must be ignored.

    :param client_socket: Socket from which message was received
    :type client_socket: ``socket``
    :param identity: Identity associated with socket
    :type identity: ``Identity`` or ``None``
    :param message: Parsed message received from socket
    :type message: ``Message``
    :return: True if message command is NICK, False otherwise
    :rtype: ``bool``
    """

    if message.command is not Command.NICK:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info:
        logging.info("client connecting without PASS, adding SessionInfo")
        server.register_local_connection(client_socket, None, "")
        session_info = server._sessions.get_info(client_socket)
        if not session_info:
            raise ValueError("Unexpectedly didnt get session info")

    if session_info.type is SessionType.SERVER and message.params:
        server.register_external_user(message.params["nickname"], session_info)
        return

    if message.params and "nickname" in message.params:
        nickname = message.params["nickname"]
    else:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NONICKNAMEGIVEN, "*")
        return

    if not server.is_unique(nickname):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NICKCOLLISION, "*")

    session_info.nickname = nickname


def handle_user_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """Handle USER command.

    Command: USER
    Parameters: <username> <hostname> <servername> <real_name>

    The USER message is used at the beginning of connection to specify
    the username, hostname, servername and realname of new user. It is
    also used in communication between servers to indicate new user
    arriving on IRC, since only after both USER and NICK have been
    received from a client does a user become registered.

    :param client_socket: Socket from which message was received
    :type client_socket: ``socket``
    :param identity: Identity associated with socket
    :type identity: ``Identity`` or ``None``
    :param message: Parsed message received from socket
    :param message: ``Message``
    :return: True if message command is NICK, False otherwise
    :rtype: ``bool``
    """
    if message.command is not Command.USER:
        raise ValueError("Implementation error: Wrong command type")
    if not session_info:
        # need to NICK command first
        RoutingManager.respond_client_error(client_socket, Command.ERR_NONICKNAMEGIVEN)
        return

    if session_info.type == SessionType.USER:
        # already registered
        RoutingManager.respond_client_error(client_socket, Command.ERR_ALREADYREGISTRED, session_info.nickname)
    elif session_info.type == SessionType.UNKNOWN:
        # register local user
        if not session_info.nickname:
            RoutingManager.respond_client_error(client_socket, Command.ERR_NONICKNAMEGIVEN)
            return
        if message.params:
            session_info.username = message.params["username"]
            session_info.realname = message.params["realname"]
            address = f"{message.params['hostname']}@{message.params['servername']}"
            session_info.type = SessionType.USER
        else:
            RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, session_info.nickname)
            return

        if not server.password_handler.valid_user_password(address, session_info.password):
            logging.info(f"Incorrect password given for {session_info.username}: {session_info.password}")
            RoutingManager.respond_client_error(client_socket, Command.ERR_PASSWDMISMATCH, session_info.nickname)
            server.remove_local_user(client_socket, session_info)
            return

        server.register_local_user(client_socket, session_info)
        logging.info(f"Registered: {session_info}")

        RoutingManager.respond_client(
            client_socket, command=Command.RPL_WELCOME, nickname=session_info.nickname, recepient=session_info.nickname
        )
        # TODO: notify other servers of new user
    elif session_info.type == SessionType.EXTERNAL_USER:
        # TODO: register new external user arrival
        raise NotImplementedError("Registering users from other servers not implemented")


def handle_server_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    if message.command is not Command.SERVER:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info:
        logging.info("server registered without PASS, adding SessionInfo")
        server.register_local_connection(client_socket, None, "")
        session_info = server._sessions.get_info(client_socket)
        if not session_info:
            return

    if message.params and "servername" in message.params:
        nickname = message.params["servername"]
    else:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NONICKNAMEGIVEN)
        return

    if not message.prefix:
        print("server message has no prefix")
        return

    # 1. we made the connection, the server responds with more info about itself
    # 2. OR we are getting info about another server on the network
    if session_info.type == SessionType.SERVER:
        print("got SERVER message from existing server")

        if session_info.nickname != message.params["servername"]:

            # this is a relayed message (other server giving us info about itself, this should NOT happen)
            if not server._users.get_server(message.params["servername"]):
                # we do not know this server, register it and keep broadcasting
                logging.info(
                    f"got relayed server information about {message.params['servername']} from {session_info.nickname}, the server is {message.params['hopcount']} hops away"
                )
                server.register_server(message.params["servername"], int(message.params["hopcount"]))
            # we know this server already, just relay
            return

        print(f"connected server has identified itself as: {session_info.nickname}")

        # if server is responding with this to SERVER msg:
        session_info.nickname = nickname
        session_info.hops = int(message.params["hopcount"])
        logging.info("Registered new server")

        # give the server our known users
        return

    elif session_info.type != SessionType.UNKNOWN:
        raise ValueError("Received SERVER command from registered user!")

    session_info.type = SessionType.SERVER

    if not server.is_unique(nickname):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NICKCOLLISION)

    if message.params and "hopcount" in message.params:
        hop_count = message.params["hopcount"]
    else:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, session_info.nickname)
        return

    session_info.nickname = nickname
    session_info.hops = int(hop_count)

    server.register_server(session_info.nickname, session_info.hops)
    logging.info(f"Registered: {session_info}")

    RoutingManager.send_command(
        client_socket,
        Prefix(server.nickname),
        command=Command.SERVER,
        servername=server.nickname,
        hopcount=hop_count,
        trailing="Server desc placeholder",
    )
    helpers.send_known_servers(session_info.nickname, client_socket, server)
    helpers.broadcast_server_to_neighbours(server, message)


def handle_privmsg_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved PRIVMSG command

    Command: PRIVMSG
        Parameters: <receiver>{,<receiver>} <text to be sent>

    Numeric Replies:
    - ERR_NOTREGISTERED
    - ERR_NOSUCHNICK
    - ERR_NOSUCHCHANNEL
    - ERR_NOTONCHANNEL

    Forwards message to user or channel
    Checks if: user is known(session info), required channel name is present
    Delegates forwarding message to routing manager


    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :raises ValueError: In cases that should not be possible
    :type message: ``Message``
    :return: None
    :rtype: None
    """
    if message.command is not Command.PRIVMSG:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info or not session_info.registered():
        RoutingManager.respond_client_error(client_socket, Command.ERR_NOTREGISTERED)
        return

    if session_info.type == SessionType.USER:
        message.prefix = Prefix(session_info.nickname, session_info.username, server.nickname)

    # can be either nickname or servername
    receiver = None
    if message.params:
        receiver = message.params["receiver"]

    if not receiver:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NONICKNAMEGIVEN, session_info.nickname)
        return

    message_to_send = message

    try:
        if IRCValidator.validate_channel(receiver):
            channel = server._channels.get_channel(receiver)
            if session_info.nickname not in channel.users:
                RoutingManager.respond_client_error(
                    client_socket, Command.ERR_NOTONCHANNEL, session_info.nickname, channel=receiver
                )
                return
            RoutingManager.send_to_channel(server, channel, message_to_send)
            return

        receiver_user = server._users.get_user(receiver)
        if not receiver_user:
            RoutingManager.respond_client_error(client_socket, Command.ERR_NOSUCHCHANNEL, session_info.nickname)
            return
        RoutingManager.forward_to_user(server, receiver, message_to_send)
    except NoSuchNick:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NOSUCHNICK, session_info.nickname)
    except NoSuchChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOSUCHCHANNEL, recepient=session_info.nickname, channel=receiver
        )


def handle_ping_command(
    _: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved PING command

    Responfing with PONG to notify that server is alive

    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :return: None
    :rtype: None
    """

    if not session_info or not session_info.registered():
        return

    receiver = message.params["receiver"] if message.params else ""  # this is us

    RoutingManager.send_command(client_socket, command=Command.PONG, receivedby=receiver)


def handle_join_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved JOIN command

    Command: JOIN
        Parameters: <channel>

    Numeric Replies:
    - ERR_NEEDMOREPARAMS
    - ERR_NOSUCHCHANNEL
    - RPL_TOPIC and RPL_NAMREPLY


    Checks if: user is known(session info), required channel name is present
    Delegates performing JOIN operation to channel manager.
    If channel did not exist it is created and user becomes channel operator
    If JOIN operation performed correctly:
    - sends to user a pair of: TOPIC, NAMREPLY:
        - NAMREPLY containis channel name and nicknames of users on channel separated by spaces
        - TOPIC contains channel name and channel topic
    - notifies user on channel about joining of new user


    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :return: None
    :rtype: None
    """

    if not message.params or not session_info:
        return
    channel_name = message.params["channel"]
    if not channel_name:
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS, recepient=session_info.nickname)
    try:
        server._channels.join(channel_name, session_info.nickname)
        names = server._channels.get_names(channel_name)
        symbol = server._channels.get_symbol(channel_name)
        topic = server._channels.get_topic(channel_name)
    except NoSuchChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOSUCHCHANNEL, recepient=session_info.nickname, channel=channel_name
        )

    RoutingManager.respond_client(
        client_socket,
        prefix=None,
        command=Command.RPL_TOPIC,
        recepient=session_info.nickname,
        channel=channel_name,
        trailing=topic,
    )
    RoutingManager.respond_client(
        client_socket,
        prefix=None,
        command=Command.RPL_NAMREPLY,
        recepient=session_info.nickname,
        symbol=symbol,
        channel=channel_name,
        trailing=names,
    )
    channel = server._channels.get_channel(channel_name)
    message.prefix = Prefix(session_info.nickname, session_info.username, server.nickname)

    RoutingManager.send_to_channel(server, channel, message)


def handle_names_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved NAMES command

    Checks if: user is known(session info), required channel name is present
    Gets names form requested channel

    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :raises ValueError: In cases that should not be possible
    :return: None
    :rtype: None
    """
    if message.command is not Command.NAMES:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info:
        raise ValueError("Cannot call names if not registered")

    if not message.params or not message.params["channel"]:
        # TODO if channel not passed return all visible channels
        raise NotImplementedError("Not yet implemented")

    channel_name = message.params["channel"]
    try:
        names = server._channels.get_names(channel_name)
        symbol = server._channels.get_symbol(channel_name)
    except NoSuchChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOSUCHCHANNEL, recepient=session_info.nickname, channel=channel_name
        )

    RoutingManager.respond_client(
        client_socket,
        prefix=None,
        command=Command.RPL_NAMREPLY,
        recepient=session_info.nickname,
        channel=channel_name,
        symbol=symbol,
        trailing=names,
    )

    RoutingManager.respond_client(
        client_socket,
        prefix=None,
        command=Command.RPL_ENDOFNAMES,
        recepient=session_info.nickname,
        channel=channel_name,
    )


def handle_part_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved PART command

    Command: PART
        Parameters: <channel>

    Numeric Replies:
    - ERR_NEEDMOREPARAMS
    - ERR_NOSUCHCHANNEL
    - ERR_NOTONCHANNEL

    Checks if: user is known(session info), required channel name is present
    Delegates performing PART operation to channel manager.
    If PART operation performed correctly, notifies channel users and user kicked from channel.

    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :raises ValueError: In cases that should not be possible
    :return: None
    :rtype: None
    """
    if message.command is not Command.PART:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info:
        raise ValueError("Operation not allowed for unknown")

    if not message.params or not (channel_name := message.params["channel"]):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS)
        return
    prefix = Prefix(session_info.nickname, session_info.username, server.nickname)
    message.prefix = prefix
    try:
        server._channels.part_from_channel(channel_name, session_info.nickname)
        channel = server._channels.get_channel(channel_name)
        RoutingManager.send_to_channel(server, channel, message)
        RoutingManager.forward_to_user(server, session_info.nickname, message)
    except NoSuchChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOSUCHCHANNEL, recepient=session_info.nickname, channel=channel_name
        )
    except NotOnChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOTONCHANNEL, recepient=session_info.nickname, channel=channel_name
        )


def handle_kick_command(
    server: IRCServer, client_socket: socket.socket, session_info: SessionInfo | None, message: Message
) -> None:
    """
    Handles recieved KICK command

    Command: KICK
    Parameters: <channel> <user>

    Numeric Replies:
    - ERR_NEEDMOREPARAMS
    - ERR_NOSUCHCHANNEL
    - ERR_CHANOPRIVSNEEDED
    - ERR_NOTONCHANNEL

    Checks if: user is known(session info), required command parameters present(channel, nickname)
    Delegates performing KICK operation to channel manager.
    If KICK operation performed correctly, notifies channel users and user kicked from channel.

    :param server: Current server instance
    :type server: ``IRCServer``
    :param client_socket: Socket from which the message was received
    :type client_socket: ``socket.socket``
    :param session_info: Session information instance associated with the client socket
    :type session_info: ``SessionInfo | None``
    :param message: Parsed message received from the socket
    :type message: ``Message``
    :raises ValueError: In cases that should not be possible
    :return: None
    :rtype: None
    """
    if message.command is not Command.KICK:
        raise ValueError("Implementation error: Wrong command type")

    if not session_info:
        raise ValueError("Operation not allowed for unknown")

    if (
        not message.params
        or not (channel_name := message.params["channel"])
        or not (kicked_nick := message.params["nickname"])
    ):
        RoutingManager.respond_client_error(client_socket, Command.ERR_NEEDMOREPARAMS)
        return

    prefix = Prefix(session_info.nickname, session_info.username, server.nickname)
    message.prefix = prefix

    try:
        server._channels.kick(channel_name, session_info.nickname, kicked_nick)
        channel = server._channels.get_channel(channel_name)
        RoutingManager.send_to_channel(server, channel, message)
        RoutingManager.forward_to_user(server, kicked_nick, message)
    except NoSuchChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOSUCHCHANNEL, recepient=session_info.nickname, channel=channel_name
        )
    except NotOnChannel:
        RoutingManager.respond_client_error(
            client_socket, Command.ERR_NOTONCHANNEL, recepient=session_info.nickname, channel=channel_name
        )
    except ChanopPrivIsNeeded:
        RoutingManager.respond_client_error(
            client_socket,
            Command.ERR_CHANOPRIVSNEEDED,
            recepient=session_info.nickname,
            channel=channel_name,
        )


CMD_FUNCTIONS = {
    Command.PASS: handle_pass_command,
    Command.NICK: handle_nick_command,
    Command.USER: handle_user_command,
    Command.SERVER: handle_server_command,
    Command.PRIVMSG: handle_privmsg_command,
    Command.QUIT: handle_quit_command,
    Command.PING: handle_ping_command,
    Command.JOIN: handle_join_command,
    Command.OPER: handle_oper_command,
    Command.NAMES: handle_names_command,
    Command.PART: handle_part_command,
    Command.KICK: handle_kick_command,
    Command.CONNECT: handle_connect_command,
}
