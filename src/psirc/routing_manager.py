import socket
import logging

from psirc.message import Message, Prefix
from psirc.response_params import parametrize
from psirc.client_manager import ClientManager
from psirc.client import LocalUser
from psirc.channel import Channel
from psirc.defines.responses import Command
from psirc.defines.exceptions import NoSuchNick


class RoutingManager:

    @staticmethod
    def send_response(client_socket: socket.socket, message: Message) -> None:
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
        if command.value >= 1000:
            print("DEV: WARNING! IRC Command passed in numeric reply function")
        response = Message(prefix=prefix, command=command, params=parametrize(command, **kwargs, recepient=recepient))
        cls.send_response(client_socket, response)

    @classmethod
    def send_command(
        cls, peer_socket: socket.socket, prefix: Prefix | None = None, *, command: Command, **kwargs: str
    ) -> None:
        message = Message(prefix=prefix, command=command, params=parametrize(command, **kwargs))
        cls.send_response(peer_socket, message)

    @classmethod
    def respond_client_error(cls, client_socket: socket.socket, error_type: Command, recepient: str = "*") -> None:
        message_error = Message(
            prefix=None,
            command=error_type,
            params=parametrize(error_type, recepient=recepient),
        )
        print(message_error)
        cls.send_response(client_socket, message_error)

    @staticmethod
    def send_to_user(receiver_nick: str, message: Message, client_manager: ClientManager) -> None:
        # for now only sends to local
        receiver = client_manager.get_user(receiver_nick)
        if not receiver:
            logging.warning(f"No user with nickname: {receiver_nick}")
            raise NoSuchNick("No user with given nickname")
        if isinstance(receiver, LocalUser):
            logging.info(f"Forwarding private message: {message}")
            receiver.socket.send(str(message).encode())
        else:
            # TODO: forward to server
            raise NotImplementedError("send to user external")
        return

    @staticmethod
    def send_to_channel(channel: Channel, message: Message, client_manager: ClientManager) -> None:
        # for now only sends to local
        encoded_message = str(message).encode()
        external_users = []
        logging.info(f"Forwarding private message: {message}")
        for nickname in channel.users:
            if message.prefix and nickname == message.prefix.sender:
                continue

            user = client_manager.get_user(nickname)
            if isinstance(user, LocalUser):
                user.socket.send(encoded_message)
            else:
                external_users.append(user)
        # TODO: forward to servers
