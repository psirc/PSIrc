# response_params.py
#
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
from psirc.defines.responses import Command

CMD_PARAMS = {
    Command.RPL_AWAY: ["nick", "away_message"],
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
    Command.PRIVMSG: ["receiver", "text"],
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


def parametrize(response: Command, **kwargs: str) -> Params | None:
    """
    Get a valid Params object for a given reply/error
    """
    params = []
    if response in CMD_PARAMS:
        for param in CMD_PARAMS[response]:
            try:
                params.append(kwargs[param])
                break
            except KeyError:
                print(f"Response {response.name} requires: {[param for param in CMD_PARAMS[response]]} as arguments")
                return None
    if response in CMD_MESSAGES:
        params.append(f":{CMD_MESSAGES[response]}")

    return Params(params)
