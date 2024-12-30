from psirc.message_parser import MessageParser
from psirc.message import Message, Prefix, Params
import pytest


@pytest.fixture
def parser():
    return MessageParser


# @pytest.mark.parametrize(("text", "command"), [("fdfdfd", "fdfdfd")])
# def test_parse_command(parser, text, command):
#     assert True
