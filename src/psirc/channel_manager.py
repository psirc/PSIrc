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
        :return: None
        :rtype: None
        """
        if channel_name not in self.channels.keys():
            raise NoSuchChannel
        self.channels[channel_name].forward_message(self.message_sender, message)

    def join(self, channel_name: str, nickname: str, key: str = "") -> None:
        """Handle/delegate JOIN - join the channel
        If channel of declared name doesnt exits, create one

        :param channel_name: name of the channet to which the message is sent
        :type channel_name: ``str``
        :param message: message which is being forwarded
        :type message: ``Message``
        :return: None
        :rtype: None
        """
        if channel_name not in self.channel_names.keys():
            self._create_channel(channel_name, nickname)
        else:
            self.channel_names[channel_name].join(nickname, key)

    def _create_channel(self, channel_name: str, nickname: str) -> None:
        self.channels[channel_name] = Channel(channel_name, nickname)
        return True
