import re
from psirc.message import Message, Prefix
from psirc.irc_validator import IRCValidator


class MessageParser:
    message_regex = r"^(:(?P<prefix>\S+)\s)?(?P<cmd>\S+)(\s(?P<params>.*?))?(?:\s:(?P<trail>.*))?$"
    prefix_regex = r"^(?P<nick>[^\s!.@]+)(!(?P<user>[^\s@!]+))?(@(?P<host>\S+))?$|^(?P<servername>\S+)$"

    @classmethod
    def _parse_prefix(cls, prefix: str) -> Prefix | None:
        match = re.match(cls.prefix_regex, prefix)

        if sender := match.group("servername"):
            return Prefix(sender) if IRCValidator.validate_host(sender) else None

        nick, user, host = match.group("nick", "user", "host")
        print(nick)

        if all((IRCValidator.validate_nick(nick), host is None or IRCValidator.validate_host(host))):
            return Prefix(nick, user or "", host or "")

    @classmethod
    def parse_message(cls, data: str) -> Message:
        match = re.match(cls.message_regex, data)
        prefix, command, params, trailing = match.group("prefix", "cmd", "params", "trail")

        prefix = cls._parse_prefix(prefix) if prefix else None
        print(prefix)
        print(command)
        print(params)
        print(trailing)
        return Message(prefix=prefix, command="", params=None)
