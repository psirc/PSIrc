import socket

from psirc.server import IRCServer
from psirc.routing_manager import RoutingManager
from psirc.defines.responses import Command


def send_local_user_nicks(client_socket: socket.socket, server: IRCServer, hop_count: str) -> None:
    for user in server.get_local_users():
        RoutingManager.send_command(client_socket, command=Command.NICK, nickname=user, hopcount=hop_count)
