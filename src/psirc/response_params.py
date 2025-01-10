# response_params.py
#
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
from psirc.defines.responses import Command

CMD_PARAMS = {
    Command.RPL_AWAY: ["nickname", "trailing"],
    Command.RPL_WHOISUSER: ["nickname", "user", "host", "real_name"],
    Command.RPL_WHOISSERVER: ["nickname", "server", "server_info"],
    Command.RPL_WHOISOPERATOR: ["nickname"],
    Command.RPL_WHOISIDLE: ["nickname", "seconds_idle"],
    Command.RPL_ENDOFWHOIS: ["nickname"],
    Command.RPL_WHOISCHANNELS: ["nickname", "channel"],
    Command.ERR_NOSUCHNICK: ["nickname"],
    Command.ERR_NOSUCHSERVER: ["server"],
    Command.ERR_CANNOTSENDTOCHAN: ["channel"],
    Command.ERR_TOOMANYCHANNELS: ["channel"],
    Command.ERR_WASNOSUCHNICK: ["nickname"],
    Command.ERR_TOOMANYTARGETS: ["target"],
    Command.PASS: ["password"],
    Command.NICK: ["nickname"],
    Command.USER: ["username", "hostname", "servername", "realname"],
    Command.PRIVMSG: ["receiver", "trailing"],
    Command.PING: ["trailing"],
    Command.JOIN: ["channel"],
    Command.CAP: ["param", "spec"]
}

CMD_MESSAGES = {
    Command.RPL_UNAWAY: "You are no longer marked as being away",
    Command.RPL_WHOISOPERATOR: "Is a server Operator",
    Command.RPL_WHOISIDLE: "seconds idle",
    Command.RPL_ENDOFWHOIS: "end of /WHOIS list",
    Command.ERR_NOSUCHNICK: "No such nick/channel",
    Command.ERR_NOSUCHSERVER: "No such server",
    Command.ERR_NOSUCHCHANNEL: "No such channel",
    Command.ERR_CANNOTSENDTOCHAN: "Cannot send to channel",
    Command.ERR_TOOMANYCHANNELS: "You have joined too many channels",
    Command.ERR_WASNOSUCHNICK: "There was no such nickname",
    Command.ERR_TOOMANYTARGETS: "Duplicate recipients, No message delivered",
    Command.ERR_NONICKNAMEGIVEN: "No nickname given",
    Command.ERR_NOORIGIN: "No origin specified",
    Command.ERR_NORECIPIENT: "No recipient given",
    Command.ERR_NOTEXTTOSEND: "No text to send",
}


def parametrize(command: Command, **kwargs: str) -> Params | None:
    """
    Get a valid Params object for a given reply/error
    """
    params = {}
    if command in CMD_PARAMS:
        for param in CMD_PARAMS[command]:
            try:
                params[param] = kwargs[param]
            except KeyError:
                print(f"Response {command.name} requires: {[param for param in CMD_PARAMS[command]]} as arguments")
                return None
    if command in CMD_MESSAGES:
        params["response"] = f":{CMD_MESSAGES[command]}"

    return Params(params)
