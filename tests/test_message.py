from psirc.message import Prefix, Params, Message
import pytest

Prefix.sender = "example.com"


def test_prefix_sender():
    assert Prefix.sender == "example.com"


def test_prefix_string():
    p = Prefix()
    assert str(p) == ":example.com "


def test_prefix_string_name():
    p = Prefix("john")
    assert str(p) == ":example.com!john "


def test_prefix_host():
    p = Prefix("john", "host.net")
    assert str(p) == ":example.com!john@host.net "


def test_message():
    p = Prefix()
    cmd = "PRIVMSG"
    params = Params(["#channel", ":Hello!"])
    msg = Message(prefix=p, command=cmd, params=params)
    assert str(msg) == ":example.com PRIVMSG #channel :Hello!\r\n"


def test_message_with_host():
    p = Prefix("john", "host.net")
    cmd = "PRIVMSG"
    params = Params(["#channel", ":Hello!"])
    msg = Message(prefix=p, command=cmd, params=params)
    assert str(msg) == ":example.com!john@host.net PRIVMSG #channel :Hello!\r\n"
