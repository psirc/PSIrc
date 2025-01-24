from enum import Enum


class Command(Enum):
    # ----------- REPLIES ------------
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
    RPL_TOPIC = 332
    # Names
    RPL_NAMREPLY = 353
    RPL_ENDOFNAMES = 366
    RPL_YOUREOPER = 381

    # ------------ ERRORS -------------
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
    ERR_NICKCOLLISION = 436
    ERR_NOTONCHANNEL = 442
    ERR_NOTREGISTERED = 451

    ERR_NEEDMOREPARAMS = 461
    ERR_ALREADYREGISTRED = 462
    ERR_PASSWDMISMATCH = 464

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
    PONG = 1009

    QUIT = 1010
    CONNECT = 1011
    NAMES = 1012
    PART = 1013

    CAP = 2000

    def __str__(self) -> str:
        return f"{self.value:03}" if self.value < 1000 else self.name


# TODO: fill up the list
