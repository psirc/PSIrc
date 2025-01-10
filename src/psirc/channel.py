from psirc.defines.exceptions import BannedFromChannel, BadChannelKey
from psirc.message import Message
from psirc.message_sender import MessageSender


class Channel:
    """Class representing channel
    Is used to perform channel operations
    """

    def __init__(self, name: str, chanop_nickname: str) -> None:
        self.name = name
        self.chanops = [chanop_nickname]
        self.users = [chanop_nickname]
        self.banned_users = []
        self.key = ""

    def join(self, nickname: str, key: str = "") -> None:
        # TODO: add better handling banned users, and incorrect password
        if nickname in self.banned_users:
            raise BannedFromChannel

        if key != self.key:
            raise BadChannelKey

        self.users.append(nickname)

    def kick(self, nickname: str) -> bool:
        if nickname in self.users:
            self.users.remove(nickname)
            return True
        return False

    def forward_message(self, message_sender: MessageSender, message: Message) -> None:
        for nickname in self.users:
            message_sender.send_message(nickname, message)
