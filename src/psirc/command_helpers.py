import socket

from psirc.server import IRCServer
from psirc.routing_manager import RoutingManager
from psirc.defines.responses import Command
from psirc.message import Message, Prefix
from psirc.session_info import SessionType


def send_local_user_nicks(client_socket: socket.socket, server: IRCServer, hop_count: str) -> None:
    for user in server.get_local_users():
        print(f"sending local user: {user}")
        RoutingManager.send_command(client_socket, command=Command.NICK, nickname=user, hopcount=hop_count)


def send_external_user_nicks(client_socket: socket.socket, server: IRCServer) -> None:
    external_users = server.get_external_users()
    for user in external_users:
        print(f"external user: {user}")
        RoutingManager.send_command(client_socket, command=Command.NICK, nickname=user, hopcount=str(external_users[user]))


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


def send_known_servers(nickname: str, client_socket: socket.socket, server: IRCServer) -> None:
    servers = server._users.list_servers()
    for irc_server in servers:
        print(f"sending info on {irc_server}")
        if irc_server != nickname:
            RoutingManager.send_command(
                client_socket,
                prefix=Prefix(server.nickname),
                command=Command.SERVER,
                servername=irc_server,
                hopcount=str(servers[irc_server].hop_count + 1),
                trailing="placeholder"
            )

