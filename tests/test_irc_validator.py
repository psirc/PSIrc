from psirc.irc_validator import IRCValidator
import pytest


@pytest.mark.parametrize(
    ("nick", "expected_result"),
    [
        ("ojeju12", True),
        ("john[]", True),
        ("GrrBB1", True),
        ("Yan32Zen", True),
        ("ForK[]", True),
        ("masK{]-\\", True),
        ("HHhHH}{}^", True),
        ("bro`sds{}", True),
        ("e0", True),
        ("m1", True),
        ("cat^-^", True),
        ("bleh-db", True),
        ("doaads13", True),
        ("too-long-nickname", False),
        # including invalid special characters
        ("me#polo", False),
        ("math%12", False),
        ("(fdhh", False),
        ("mat)d", False),
        ("floor_66", False),
        ("positive+", False),
        ("eq=ual", False),
        ('quo"te', False),
        ("semi;col", False),
        ("hh:lll", False),
        ("star*98", False),
        ("fwslash/", False),
        ("dot.", False),
        ("gr<ll", False),
        ("matt>", False),
        ("carol?", False),
        ("m&m", False),
        ("victor$$", False),
        ("monkey@", False),
        ("soccer1!", False),
        ("pipe|d", False),
        # starting with character other than ascii letter
        ("1bad-st", False),
        ("2bad-st", False),
        ("3bad-st", False),
        ("4bad-st", False),
        ("5bad-st", False),
        ("6bad-st", False),
        ("7bad-st", False),
        ("8bad-st", False),
        ("9bad-st", False),
        ("0bad-st", False),
        ("*fdfd", False),
        (":gfff", False),
    ],
)
def test_validate_nickname(nick, expected_result):
    assert IRCValidator.validate_nick(nick) == expected_result


@pytest.mark.parametrize(
    ("host", "expected_result"),
    [
        ("host", True),
        ("example.net", True),
        ("many.subdomains.here.edu.pl", True),
        ("number12.edu.pl", True),
        ("correct-website.pl", True),
        ("gas78-company2.com", True),
        ("my-domain.gggg.pl", True),
        ("CAP.DOMAIN", True),
    ],
)
def test_validate_host(host, expected_result):
    assert IRCValidator.validate_host(host) == expected_result


@pytest.mark.parametrize(
    ("channel", "expected_result"),
    [("#channel", True), ("&correct23", True), ("!incorrect", False), ("#channel has spaces", False)],
)
def test_validate_channel(channel, expected_result):
    assert IRCValidator.validate_channel(channel) == expected_result
