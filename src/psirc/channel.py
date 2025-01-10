from psirc.defines.exceptions import BannedFromChannel, BadChannelKey, NotOnChannel
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
        """Add user with selected nickname to server.
        If user is banned raise BannedFromChannel exception
        If the channel is secured by key, and given key is wrong
        raise BadChannelKey exception


        :param channel_name: name of the channet to which the message is sent
        :type channel_name: ``str``
        :param nickname: nickname of user performing join operation
        :type nickname: ``str``
        :param key: declared key to the channel
        :type key: ``str``
        :raises BannedFromChannel: if user is banned from channel
        :raises BadChannelKey: if user tries to join server with incorrect key
        :return: None
        :rtype: None

        """
        # TODO: add better handling banned users, and incorrect password
        if nickname in self.banned_users:
            raise BannedFromChannel

        if key != self.key:
            raise BadChannelKey

        self.users.append(nickname)

    def kick(self, nickname: str) -> None:
        """Kick user from channel


        :param nickname: nickname of user performing join operation
        :type nickname: ``str``
        :raises: NotOnChannel: if user with provided nick is not on channel
        :return: None
        :rtype: None
        """
        if nickname not in self.users:
            raise NotOnChannel(f"user with nick: {nickname} is not on channel: {self.name}")

        self.users.remove(nickname)

    def forward_message(self, message_sender: MessageSender, message: Message) -> None:
        for nickname in self.users:
            message_sender.send_message(nickname, message)
