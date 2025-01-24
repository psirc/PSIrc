import socket

from psirc.server import IRCServer
from psirc.routing_manager import RoutingManager
from psirc.defines.responses import Command
from psirc.message import Message
from psirc.session_info import SessionType


def send_local_user_nicks(client_socket: socket.socket, server: IRCServer, hop_count: str) -> None:
    for user in server.get_local_users():
        RoutingManager.send_command(client_socket, command=Command.NICK, nickname=user, hopcount=hop_count)


def broadcast_server_to_neighbours(server: IRCServer, message: Message) -> None:
    server_sessions = server._sessions.get_sessions_by_type(SessionType.SERVER)
    if not message.prefix or not message.params:
        print("Tried to broadcast to neighbours but no prefix/params found!")
        return
    message.params["hopcount"] = str(int(message.params["hopcount"]) + 1)
    for peer_socket in server_sessions:
        if server_sessions[peer_socket].nickname == message.prefix.sender:
            continue
        RoutingManager.send(peer_socket, message)
