import re
from psirc.message import Message, Prefix


class MessageParser:
    message_regex = r"^(:(?P<prefix>\S+)\s)?(?P<cmd>\S+)(\s(?P<params>.*?))?(?:\s:(?P<trail>.*))?$"

    def __init__(self) -> None:
        pass

    # def _parse_prefix() -> Prefix | None:

    def parse_message(self, data: str) -> Message:
        match = re.match(self.message_regex, data)
        prefix = match.group("prefix")
        command = match.group("cmd")
        params = match.group("params")
        trailing = match.group("trail")

        print(prefix)
        print(command)
        print(params)
        print(trailing)
        return Message(prefix=None, command="", params=None)
