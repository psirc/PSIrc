import re


class IRCValidator:
    """
    Simple class to validate format of IRC components - nicks, channels, usernames
    """

    nick_regex = r"^[A-Za-z][A-Za-z0-9\-\[\]\\`^{}]{0,8}$"

    @classmethod
    def validate_nick(cls, nick: str) -> bool:
        return bool(re.match(cls.nick_regex, nick))
