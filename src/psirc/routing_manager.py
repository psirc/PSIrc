import socket
import logging

from psirc.message import Message
from psirc.user_manager import UserManager
from psirc.channel import Channel


class RoutingManager:
    @staticmethod
    def respond_client(client_socket: socket.socket, response: Message) -> None:
        client_socket.send(str(response).encode())

    @staticmethod
    def send_to_user(receiver_nick: str, message: Message, user_manager: UserManager) -> None:
        # for now only sends to local
        receiver = user_manager.get_user(receiver_nick)
        if not receiver:
            raise KeyError("Receiver not found")
        if receiver.is_local():
            logging.info(f"Forwarding private message: {message}")
            receiver.get_route().send(str(message).encode())
        else:
            # TODO: forward to server
            raise NotImplementedError("send to user external")
        return

    @staticmethod
    def send_to_channel(channel: Channel, message: Message, user_manager: UserManager) -> None:
        # for now only sends to local
        encoded_message = str(message).encode()
        external_users = []
        for nickname in channel.users:
            user = user_manager.get_user(nickname)
            if user.is_local():
                user.get_route().send(encoded_message)
            else:
                external_users.append(user)
        # TODO: forward to servers
