import logging
from psirc.defines.exceptions import BannedFromChannel, BadChannelKey, NotOnChannel, ChanopPrivIsNeeded


class Channel:
    """Class representing channel
    Is used to perform channel operations
    """

    def __init__(self, name: str, chanop_nickname: str) -> None:
        self.name = name
        self.chanops = {chanop_nickname}
        self.users = {chanop_nickname}
        self.banned_users: set[str] = set()
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

        logging.info(f"{self.name}:{nickname} joined the channel")
        self.users.add(nickname)

    def kick(self, nickname: str, kicked_nick: str) -> None:
        """Kick user from channel

        :param nickname: nickname of user performing KICK operation
        :type nickname: str
        :param kicked_nick: nickname of user to be kicked
        :type kicked_nick: ``str``
        :raises: ChanopPrivIsNeeded: if user trying to perform operation does not have needed privileges
        :raises: NotOnChannel: if user with provided nick is not on channel
        :return: None
        :rtype: None
        """
        if not self.is_chanop(nickname):
            raise ChanopPrivIsNeeded(
                f"Channel operator's privileges needed to perform KICK operation. {nickname} has no such privileges."
            )
        logging.info(f"Kicking {nickname} from channel {self.name}")
        self.part(kicked_nick)

    def part(self, nickname: str) -> None:
        """Part from channel

        :param nickname: nickname of user departing from channel
        :type nickname: str
        :raises: NotOnChannel: if user with provided nick is not on channel
        :return: None
        :rtype: None
        """
        if not self.is_in_channel(nickname):
            raise NotOnChannel(f"user with nick: {nickname} is not on channel: {self.name}")
        self.users.remove(nickname)
        if self.is_chanop(nickname):
            self.chanops.remove(nickname)

        logging.info(f"{nickname} parted from channel: {self.name}")

    def is_in_channel(self, nickname: str) -> bool:
        return nickname in self.users

    def is_chanop(self, nickname: str) -> bool:
        return nickname in self.chanops

    def names(self) -> str:
        return " ".join((("@" + nickname if nickname in self.chanops else "+" + nickname) for nickname in self.users))
