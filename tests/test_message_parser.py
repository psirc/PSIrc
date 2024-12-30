from psirc.message_parser import MessageParser
from psirc.message import Prefix
import pytest


@pytest.mark.parametrize(
    ("text", "prefix"),
    [
        (":sender.com JOIN", Prefix("sender.com")),
        (":ojeju12 NICK newnick", Prefix("ojeju12")),
        ("PRIVMSG #fishing :Going fishing today!", None),
        (":slc32!matt@hostname.net PRIVMSG #cs2 :playing inferno now", Prefix("slc32", "matt", "hostname.net")),
        (":subnet.example.com PING client1", Prefix("subnet.example.com")),
    ],
)
def test_parse_prefix(text, prefix):
    assert prefix == MessageParser.parse_message(text).prefix
