# response_params.py
#
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
from psirc.defines.responses import Response

CMD_PARAMS = {
    Response.AWAY: ["nick", "away_message"],
    Response.WHOISUSER: ["nick", "user", "host", "real_name"],
    Response.WHOISSERVER: ["nick", "server", "server_info"],
    Response.WHOISOPERATOR: ["nick"],
    Response.WHOISIDLE: ["nick", "seconds_idle"],
    Response.ENDOFWHOIS: ["nick"],
    Response.WHOISCHANNELS: ["nick", "channel"],
    Response.NOSUCHNICK: ["nick"],
    Response.NOSUCHSERVER: ["server"],
    Response.CANNOTSENDTOCHAN: ["channel"],
    Response.TOOMANYCHANNELS: ["channel"],
    Response.WASNOSUCHNICK: ["nick"],
    Response.TOOMANYTARGETS: ["target"],
}

CMD_MESSAGES = {
    Response.UNAWAY: "You are no longer marked as being away",
    Response.WHOISOPERATOR: "Is a server Operator",
    Response.WHOISIDLE: "seconds idle",
    Response.ENDOFWHOIS: "end of /WHOIS list",
    Response.NOSUCHNICK: "No such nick/channel",
    Response.NOSUCHSERVER: "No such server",
    Response.NOSUCHCHANNEL: "No such channel",
    Response.CANNOTSENDTOCHAN: "Cannot send to channel",
    Response.TOOMANYCHANNELS: "You have joined too many channels",
    Response.WASNOSUCHNICK: "There was no such nickname",
    Response.TOOMANYTARGETS: "Duplicate recipients, No message delivered",
    Response.NOORIGIN: "No origin specified",
    Response.NORECIPIENT: "No recipient given",
    Response.NOTEXTTOSEND: "No text to send",
}


def parametrize(response: int, **kwargs: str) -> Params:
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
                print(f"Response {response.NAME} requires: {[param for param in CMD_PARAMS[response]]} as arguments")
    if response in CMD_MESSAGES:
        params.append(f":{CMD_MESSAGES[response]}")

    return Params(params)
