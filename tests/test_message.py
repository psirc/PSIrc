from psirc.message import Prefix, Params, Message
import pytest

Prefix.sender = "example.com"


@pytest.fixture
def server_prefix():
    return Prefix("example.com")


@pytest.mark.parametrize(
    ("sender", "user", "host"),
    [
        ("example.com", "", ""),
        ("ojeju12", "lukasz", "host1"),
        ("maciek32", "maciej", "host2"),
        ("foo3254", "john", "johnhost"),
        ("foo.com", "", ""),
    ],
)
def test_prefix(sender, user, host):
    prefix = Prefix(sender, user, host)
    assert prefix.sender == sender
    assert prefix.user == user
    assert host == host


@pytest.mark.parametrize(
    ("prefix", "expected_str"),
    [
        (Prefix("example.com"), ":example.com"),
        (Prefix("ojeju12", "lukasz", "host1"), ":ojeju12!lukasz@host1"),
        (Prefix("maciek32", "maciej", "host2"), ":maciek32!maciej@host2"),
        (Prefix("foo3254", "john", "johnhost"), ":foo3254!john@johnhost"),
        (Prefix("foo.com", "", ""), ":foo.com"),
    ],
)
def test_prefix_string(prefix, expected_str):
    assert str(prefix) == expected_str
