import socket
import logging

from psirc.message import Message, Prefix
from psirc.response_params import parametrize
from psirc.server import IRCServer
from psirc.client import LocalUser, ExternalUser
from psirc.channel import Channel
from psirc.defines.responses import Command
from psirc.defines.exceptions import NoSuchNick


class RoutingManager:

    @staticmethod
    def send(client_socket: socket.socket, message: Message) -> None:
        """Send a message to a local client or local server via the specified socket.

        :param client_socket: client socket.
        :type client_socket: ``socket.socket``
        :param message: message to send.
        :type message: ``Message``
        """
        client_socket.send(str(message).encode())

    @classmethod
    def respond_client(
        cls,
        client_socket: socket.socket,
        prefix: Prefix | None = None,
        *,
        command: Command,
        recepient: str | None,
        **kwargs: str,
    ) -> None:
        """Respond to a local client with a specific command and parameters.

        :param client_socket: client's socket.
        :type client_socket: ``socket.socket``
        :param prefix: prefix of the response (optional).
        :type prefix: ``Prefix | None``
        :param command: IRC command to send.
        :type command: ``Command``
        :param recepient: nick of recipient of the response (optional).
        :type recepient: ``str | None``
        :param kwargs: Additional parameters for the response.
        :type kwargs: ``dict[str, str]``
        """
        if command.value >= 1000:
            logging.warning("IRC Command passed in numeric reply function")
        response = Message(prefix=prefix, command=command, params=parametrize(command, **kwargs, recepient=recepient))
        logging.info(f"Responding to client:{response}")
        cls.send(client_socket, response)

    @classmethod
    def send_command(
        cls, peer_socket: socket.socket, prefix: Prefix | None = None, *, command: Command, **kwargs: str
    ) -> None:
        """Send a command message to a server or client.

        :param peer_socket: socket to send to
        :type peer_socket: ``socket.socket``
        :param prefix: prefix of the message (optional).
        :type prefix: ``Prefix | None``
        :param command: IRC command to send.
        :type command: ``Command``
        :param kwargs: Additional parameters for the message.
        :type kwargs: ``dict[str, str]``
        """
        message = Message(prefix=prefix, command=command, params=parametrize(command, **kwargs))
        cls.send(peer_socket, message)

    @classmethod
    def respond_client_error(
        cls, client_socket: socket.socket, error_type: Command, recepient: str = "*", **kwargs: str
    ) -> None:
        """Send an error response to a client.

        :param client_socket: client socket.
        :type client_socket: ``socket.socket``
        :param error_type: type of error to send.
        :type error_type: ``Command``
        :param recepient: recipient of the error response (default: "*").
        :type recepient: ``str``
        :param kwargs: Additional parameters for the error response.
        :type kwargs: ``dict[str, str]``
        """
        message_error = Message(
            prefix=None,
            command=error_type,
            params=parametrize(error_type, recepient=recepient, **kwargs),
        )
        logging.info(f"Responding to client with error: {message_error}")
        cls.send(client_socket, message_error)

    @classmethod
    def forward_to_user(cls, server: IRCServer, receiver_nick: str, message: Message) -> None:
        """Forward a message to a specific user.

        :param server: IRC server instance.
        :type server: ``IRCServer``
        :param receiver_nick: nickname of the receiving user.
        :type receiver_nick: ``str``
        :param message: message to forward.
        :type message: ``Message``
        :raises NoSuchNick: If the user does not exist.
        :raises ValueError: If an internal error occurs.
        """
        receiver = server._users.get_user(receiver_nick)

        if not receiver:
            logging.warning(f"No user with nickname: {receiver_nick}")
            raise NoSuchNick("No user with given nickname")

        logging.info(f"Forwarding private message: {message}")
        if isinstance(receiver, LocalUser):
            cls.send(receiver.socket, message)
        elif isinstance(receiver, ExternalUser):
            next_hop_sock = server._sessions.get_socket(receiver.location)
            if not next_hop_sock:
                raise ValueError("Implementation error inside the code")
            cls.send(next_hop_sock, message)
        else:
            raise ValueError("Implementation error inside the code")

    @classmethod
    def send_to_channel(cls, server: IRCServer, channel: Channel, message: Message) -> None:
        """Send message to channel members.

        Doesn't send message to local user if local user sent the message or to closest server from which message was received.

        :param server: IRC server instance.
        :type server: ``IRCServer``
        :param channel: channel to send the message to.
        :type channel: ``Channel``
        :param message: message to send.
        :type message: ``Message``
        :raises ValueError: If the sender or message prefix is missing.
        :raises NoSuchNick: If a user in the channel does not exist.
        """
        logging.info(f"Forwarding message to channel: {message}")
        if not message.prefix:
            raise ValueError("Implementation error inside the code")
        sender_nick = message.prefix.sender
        if not sender_nick:
            raise ValueError("Missing sender nick in send to channel")
        sender = server._users.get_user(sender_nick)
        if not sender:
            raise ValueError("Sender not a registered user")

        # Dont resend message to server. Finding the sender socket
        sender_socket = None
        if isinstance(sender, LocalUser):
            sender_socket = server._sessions.get_socket(sender_nick)
        elif isinstance(sender, ExternalUser):
            sender_socket = server._sessions.get_socket(sender.location)
        if not sender_socket:
            raise ValueError("Cant find sender socket")

        next_hop_socks = set()
        # send to local users
        for nickname in channel.users:
            receiver = server._users.get_user(nickname)

            if not receiver:
                logging.warning(f"No user with nickname: {nickname}")
                raise NoSuchNick("No user with given nickname")

            if isinstance(receiver, LocalUser):
                if receiver.socket == sender_socket:
                    # dont send to sender
                    continue
                cls.send(receiver.socket, message)
            elif isinstance(receiver, ExternalUser):
                next_hop_sock = server._sessions.get_socket(receiver.location)
                if not next_hop_sock:
                    raise ValueError("Implementation error inside the code")
                if next_hop_sock == sender_socket:
                    # dont send to sender
                    continue
                next_hop_socks.add(next_hop_sock)
            else:
                raise ValueError("Implementation error inside the code")

        # broadcast to servers
        for next_hop_sock in next_hop_socks:
            cls.send(next_hop_sock, message)
