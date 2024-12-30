from psirc.message_parser import MessageParser
from psirc.message import Message, Prefix, Params
import pytest


@pytest.fixture
def parser():
    return MessageParser()


@pytest.mark.parametrize(
    ("text", "command"),
    [
        (":prefix JOIN", "fdfdfd"),
        (":ojeju12 NICK newnick", "eeee"),
        ("PRIVMSG #fishing :Going fishing today!", "fffff"),
    ],
)
def test_parse_command(parser, text, command):
    ret = parser.parse_message(text)
    assert True
