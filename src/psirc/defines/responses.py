from enum import Enum


class Command(Enum):
    RPL_WELCOME = 1
    RPL_NONE = 300
    RPL_USERHOST = 302

    # Away message
    RPL_AWAY = 305
    RPL_UNAWAY = 301
    RPL_NOAWAY = 305

    # WHOIS Message
    RPL_WHOISUSER = 311
    RPL_WHOISSERVER = 312
    RPL_WHOISOPERATOR = 313
    RPL_WHOISIDLE = 317
    RPL_ENDOFWHOIS = 318
    RPL_WHOISCHANNELS = 319

    # Error responses
    ERR_NOSUCHNICK = 401
    ERR_NOSUCHSERVER = 402
    ERR_NOSUCHCHANNEL = 403
    ERR_CANNOTSENDTOCHAN = 404
    ERR_TOOMANYCHANNELS = 405
    ERR_WASNOSUCHNICK = 406
    ERR_TOOMANYTARGETS = 407
    ERR_NOORIGIN = 409
    ERR_NORECIPIENT = 411
    ERR_NOTEXTTOSEND = 412

    ERR_NONICKNAMEGIVEN = 431
    ERR_NOTREGISTERED = 451

    # Responses greater than 1000
    # Representing text commands
    PASS = 1000
    NICK = 1001
    USER = 1002
    SERVER = 1003
    OPER = 1004

    JOIN = 1005
    PRIVMSG = 1007
    PING = 1008

    QUIT = 1010

    CAP = 2000

    def __str__(self) -> str:
        return f"{self.value:03}" if self.value < 1000 else self.name


# TODO: fill up the list
