import socket

from psirc.server import IRCServer
from psirc.routing_manager import RoutingManager
from psirc.message import Message
from psirc.defines.responses import Command
from psirc.response_params import parametrize


def send_local_user_nicks(client_socket: socket.socket, server: IRCServer, hop_count: str) -> None:
    for user in server.get_local_users():
        reply_nick = Message(
            prefix=None,
            command=Command.NICK,
            params=parametrize(Command.NICK, nickname=user, hopcount=str(hop_count))
        )
        RoutingManager.respond_client(client_socket, reply_nick)
