from psirc.message import Message


class MessageParser:
    def __init__(self) -> None:
        pass

    def parse_message(self, data: str) -> Message:
        prefix = None
        command = None
        params = None

        return Message(prefix, command, params)
