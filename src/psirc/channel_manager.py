import logging
from psirc.defines.exceptions import NoSuchChannel
from psirc.channel import Channel


class ChannelManager:
    """Class managing channels, and handling channel operations
    attributes:
        channels - dict[string, Channel], dict of existing channels
    """

    def __init__(self) -> None:
        self.channels: dict[str, Channel] = {}

    def join(self, channel_name: str, nickname: str, key: str = "") -> None:
        """Handle/delegate JOIN - join the channel
        If channel of declared name doesnt exits, create one

        :param channel_name: name of the channel to which the message is sent
        :type channel_name: ``str``
        :param nickname: nickname of user performing join operation
        :type nickname: ``str``
        :param key: declared key to the channel
        :type key: ``str``
        :return: None
        :rtype: None
        """
        try:
            channel = self.get_channel(channel_name)
            channel.join(nickname, key)
            logging.info(f"{nickname} joined {channel_name}")
        except NoSuchChannel:
            logging.info(f"NoSuchChanel: {channel_name}, creating...")
            self._create_channel(channel_name, nickname)

    def quit(self, nickname: str) -> None:
        check_if_empty = []
        for channel_name, channel in self.channels.items():
            if channel.is_in_channel(nickname):
                channel.part(nickname)
                check_if_empty.append(channel_name)
        for channel_name in check_if_empty:
            self._check_for_cleanup(channel_name)

    def kick(self, channel_name: str, nickname: str, kicked_nick: str) -> None:
        """Delegate KICK - kick from channel

        :param channel_name: name of the channel
        :type channel_name: ``str``
        :param nickname: nickname of user performing kick operation
        :type nickname: ``str``
        :param kicked_nick: nickname of user to be kicked
        :type kicked_nick: ``str``
        :raises NoSuchChannel: if there is no channel of the given name
        :raises: ChanopPrivIsNeeded: if user trying to perform operation does not have needed privileges
        :return: None
        :rtype: None
        """
        channel = self.get_channel(channel_name)
        channel.kick(nickname, kicked_nick)
        self._check_for_cleanup(channel_name)

    def part_from_channel(self, channel_name: str, nickname: str) -> None:
        channel = self.get_channel(channel_name)
        channel.part(nickname)
        self._check_for_cleanup(channel_name)

    def get_names(self, channel_name: str) -> str:
        channel = self.get_channel(channel_name)
        return channel.names()

    def get_symbol(self, channel_name: str) -> str:
        channel = self.get_channel(channel_name)
        return channel.channel_symbol()

    def get_topic(self, channel_name: str) -> str:
        channel = self.get_channel(channel_name)
        return channel.topic

    def get_channel(self, channel_name: str) -> Channel:
        """Get Channel with name

        :param channel_name: name of the channel to which the message is sent
        :type channel_name: ``str``
        :raises: NoSuchChannel: if channel of the given name doesnt exist
        :return: Channel instance corresponding to given name
        :rtype: Channel
        """
        if channel_name not in self.channels.keys():
            raise NoSuchChannel(f"Channel with name: {channel_name} does not exist")
        return self.channels[channel_name]

    def _check_for_cleanup(self, channel_name: str) -> None:
        if not self.get_channel(channel_name).names():
            logging.info(f"Channel: {channel_name} empty, deletng")
            del self.channels[channel_name]

    def _create_channel(self, channel_name: str, nickname: str) -> None:
        self.channels[channel_name] = Channel(channel_name, nickname)
