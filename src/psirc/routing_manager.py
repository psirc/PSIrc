import socket
import logging

from psirc.message import Message
from psirc.session_manager import SessionManager
from psirc.channel import Channel


class RoutingManager:
    @staticmethod
    def respond_client(client_socket: socket.socket, response: Message) -> None:
        client_socket.send(str(response).encode())

    @staticmethod
    def send_to_user(receiver_nick: str, message: Message, session_manager: SessionManager) -> None:
        # for now only sends to local
        receiver_socket = session_manager.get_user_socket(receiver_nick)
        if not receiver_socket:
            raise KeyError("Receiver not found")
        logging.info(f"Forwarding private message: {message}")
        receiver_socket.send(str(message).encode())
        return

    @staticmethod
    def send_to_channel(channel: Channel, message: Message, session_manager: SessionManager) -> None:
        # for now only sends to local
        encoded_message = str(message).encode()
        for nickname in channel.users:
            session_manager.get_user_socket(nickname).send(encoded_message)
