from psirc.message_parser import MessageParser
from psirc.message import Prefix, Message, Params
from psirc.defines.responses import Command
import pytest


@pytest.mark.parametrize(
    ("text", "prefix"),
    [
        (":sender.com JOIN #channel", Prefix("sender.com")),
        (":ojeju12 NICK newnick", Prefix("ojeju12")),
        ("PRIVMSG #fishing :Going fishing today!", None),
        (":slc32!matt@hostname.net PRIVMSG #cs2 :playing inferno now", Prefix("slc32", "matt", "hostname.net")),
        (":subnet.example.com PING client1", Prefix("subnet.example.com")),
        (":Nick!nikodem@dOmaIN.com PING client2", Prefix("Nick", "nikodem", "domain.com")),
    ],
)
def test_parse_prefix(text, prefix):
    msg = MessageParser.parse_message(text)
    assert isinstance(msg, Message)
    assert prefix == msg.prefix


@pytest.mark.parametrize(
    ("text", "command"),
    [
        (":sender.com JOIN #channel", Command.JOIN),
        (":ojeju12 NICK newnick", Command.NICK),
        ("PRIVMSG #fishing :Going fishing today!", Command.PRIVMSG),
        (":slc32!matt@hostname.net PRIVMSG #cs2 :playing inferno now", Command.PRIVMSG),
        (":subnet.example.com PING client1", Command.PING),
        (":Nick!nikodem@dOmaIN.com PING client2", Command.PING),
    ],
)
def test_parse_command(text, command):
    msg = MessageParser.parse_message(text)
    assert isinstance(msg, Message)
    assert command == msg.command


@pytest.mark.parametrize(
    ("text", "params"),
    [
        (":sender.com JOIN #channel", {"channel": "#channel"}),
        (":ojeju12 NICK newnick", {"nick": "newnick"}),
        ("PRIVMSG #fishing :Going fishing today!", {"receiver": "#fishing", "trailing": "Going fishing today!"}),
        (":slc32!matt@hostname.net PRIVMSG #cs2 :playing inferno now", {"receiver": "#cs2", "trailing": "playing inferno now"}),
        (":subnet.example.com PING client1", {"receiver": "client1"}),
        (":Nick!nikodem@dOmaIN.com PING client2", {"receiver": "client2"}),
    ],
)
def test_parse_params(text, params):
    msg = MessageParser.parse_message(text)
    assert isinstance(msg, Message)
    assert isinstance(msg.params, Params)
    assert params == msg.params.params
