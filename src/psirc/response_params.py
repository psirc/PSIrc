# response_params.py
#
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
from psirc.defines.responses import Command

CMD_PARAMS = {
    Command.RPL_AWAY: ["nick", "trailing"],
    Command.RPL_WHOISUSER: ["nick", "user", "host", "real_name"],
    Command.RPL_WHOISSERVER: ["nick", "server", "server_info"],
    Command.RPL_WHOISOPERATOR: ["nick"],
    Command.RPL_WHOISIDLE: ["nick", "seconds_idle"],
    Command.RPL_ENDOFWHOIS: ["nick"],
    Command.RPL_WHOISCHANNELS: ["nick", "channel"],
    Command.ERR_NOSUCHNICK: ["nick"],
    Command.ERR_NOSUCHSERVER: ["server"],
    Command.ERR_CANNOTSENDTOCHAN: ["channel"],
    Command.ERR_TOOMANYCHANNELS: ["channel"],
    Command.ERR_WASNOSUCHNICK: ["nick"],
    Command.ERR_TOOMANYTARGETS: ["target"],
    Command.NICK: ["nick"],
    Command.PRIVMSG: ["receiver", "trailing"],
    Command.PING: ["receiver"],
    Command.JOIN: ["channel"]
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
