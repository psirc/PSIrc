from psirc.defines.exceptions import NoSuchChannel
from psirc.channel import Channel
from psirc.message import Message
from psirc.message_sender import MessageSender


class ChannelManager:
    """Class managing channels, and handling channel operations
    attributes:
        channels - dict[string, Channel], dict of existing channels
        message_sender - MessageSender, instance to handle sending messages
    """

    def __init__(self, message_sender: MessageSender) -> None:
        self.channels: dict[str, Channel] = {}
        self.message_sender = message_sender

    def forward_message(self, channel_name: str, message: Message) -> None:
        """Delegate PRIVMSG handling to the channel

        :param channel_name: name of the channet to which the message is sent
        :type channel_name: ``str``
        :param message: message which is being forwarded
        :type message: ``Message``
        :raises: NoSuchChannel: if channel with declared name does not exist
        :return: None
        :rtype: None
        """
        channel = self.get_channel(channel_name)
        channel.forward_message(self.message_sender, message)

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
        except NoSuchChannel:
            self._create_channel(channel_name, nickname)

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

    def get_channel(self, channel_name: str) -> Channel:
        """Get Channel with name

        :param channel_name: name of the channel to which the message is sent
        :type channel_name: ``str``
        :raises: NoSuchChannel: if channel of the given name doesnt exist
        :return: Channel instance corresponding to given name
        :rtype: Channel
        """
        if channel_name not in self.channel_names.keys():
            raise NoSuchChannel(f"Channel with name: {channel_name} does not exist")
        return self.channels[channel_name]

    def _create_channel(self, channel_name: str, nickname: str) -> None:
        self.channels[channel_name] = Channel(channel_name, nickname)
        return True
