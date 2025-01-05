import re
import socket


class IRCValidator:
    """
    Simple class to validate format of IRC components - nicks, channels, usernames
    """

    nick_regex = r"^[A-Za-z][A-Za-z0-9\-\[\]\\`^{}]{0,8}$"
    host_regex = r"^[A-Za-z][A-Za-z0-9-]{0,22}[A-Za-z0-9](?:\.[A-Za-z][A-Za-z0-9-]{0,21}[A-Za-z0-9])*$"

    @classmethod
    def validate_nick(cls, nick: str) -> bool:
        return re.match(cls.nick_regex, nick) is not None

    @classmethod
    def validate_host(cls, host: str) -> bool:
        """
        according to RFC 952 https://datatracker.ietf.org/doc/html/rfc952
        """
        return re.match(cls.host_regex, host) is not None

    @classmethod
    def validate_ipv4_address(cls, ip_addr: str) -> bool:
        try:
            socket.inet_aton(ip_addr)
            return True
        except socket.error:
            return False
