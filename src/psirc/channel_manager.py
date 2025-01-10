from psirc.defines.exceptions import NoSuchChannel
from psirc.channel import Channel
from psirc.message import Message
from psirc.message_sender import MessageSender


class ChannelManager:
    def __init__(self, message_sender: MessageSender) -> None:
        self.channels: dict[str, Channel] = {}
        self.message_sender = message_sender

    def forward_message(self, channel_name: str, message: Message) -> None:
        if channel_name not in self.channels.keys():
            raise NoSuchChannel
        self.channels[channel_name].forward_message(self.message_sender, message)

    def join(self, channel_name: str, nickname: str, key: str = "") -> None:
        if channel_name not in self.channel_names.keys():
            self._create_channel(channel_name, nickname)
        else:
            self.channel_names[channel_name].join(nickname, key)

    def _create_channel(self, channel_name: str, nickname: str) -> None:
        self.channels[channel_name] = Channel(channel_name, nickname)
        return True
