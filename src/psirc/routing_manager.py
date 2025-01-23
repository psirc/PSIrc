import socket
import logging

from psirc.message import Message, Prefix
from psirc.response_params import parametrize
from psirc.client_manager import ClientManager
from psirc.client import LocalUser
from psirc.channel import Channel
from psirc.defines.responses import Command


class RoutingManager:

    @staticmethod
    def send_response(client_socket: socket.socket, message: Message) -> None:
        client_socket.send(str(message).encode())

    @classmethod
    def respond_client(cls, client_socket: socket.socket, prefix: Prefix | None = None, *, command: Command, **kwargs: str) -> None:
        response = Message(
            prefix=prefix,
            command=command,
            params=parametrize(command, **kwargs)
        )
        cls.send_response(client_socket, response)

    @classmethod
    def respond_client_error(cls, client_socket: socket.socket, error_type: Command) -> None:
        message_error = Message(
            prefix=None,
            command=error_type,
            params=parametrize(error_type),
        )
        cls.send_response(client_socket, message_error)

    @staticmethod
    def send_to_user(receiver_nick: str, message: Message, client_manager: ClientManager) -> None:
        # for now only sends to local
        receiver = client_manager.get_user(receiver_nick)
        if not receiver:
            raise KeyError("Receiver not found")
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
