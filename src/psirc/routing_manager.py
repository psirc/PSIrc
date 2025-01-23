import socket
import logging

from psirc.message import Message
from psirc.response_params import parametrize
from psirc.user_manager import ClientManager
from psirc.user import LocalUser
from psirc.channel import Channel
from psirc.defines.responses import Command


class RoutingManager:
    @staticmethod
    def respond_client(client_socket: socket.socket, response: Message) -> None:
        client_socket.send(str(response).encode())

    @staticmethod
    def respond_client_error(client_socket: socket.socket, error_type: Command) -> None:
        message_error = Message(
            prefix=None,
            command=error_type,
            params=parametrize(error_type),
        )
        RoutingManager.respond_client(client_socket, message_error)

    @staticmethod
    def send_to_user(receiver_nick: str, message: Message, user_manager: ClientManager) -> None:
        # for now only sends to local
        receiver = user_manager.get_user(receiver_nick)
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
    def send_to_channel(channel: Channel, message: Message, user_manager: ClientManager) -> None:
        # for now only sends to local
        encoded_message = str(message).encode()
        external_users = []
        logging.info(f"Forwarding private message: {message}")
        for nickname in channel.users:
            user = user_manager.get_user(nickname)
            if isinstance(user, LocalUser):
                user.socket.send(encoded_message)
            else:
                external_users.append(user)
        # TODO: forward to servers
