# response_params.py
# 
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
import psirc.defines.response_codes as rpl
import psirc.defines.error_codes as err

CMD_PARAMS = {
        rpl.AWAY: ["nick", "away_message"],
        rpl.WHOISUSER: ["nick", "user", "host", "real_name"],
        rpl.WHOISSERVER: ["nick", "server", "server_info"],
        rpl.WHOISOPERATOR: ["nick"],
        rpl.WHOISIDLE: ["nick", "seconds_idle"],
        rpl.ENDOFWHOIS: ["nick"],
        rpl.WHOISCHANNELS: ["nick", "channel"],
        err.NOSUCHNICK: ["nick"],
        err.NOSUCHSERVER: ["server"],
        err.CANNOTSENDTOCHAN: ["channel"],
        err.TOOMANYCHANNELS: ["channel"],
        err.WASNOSUCHNICK: ["nick"],
        err.TOOMANYTARGETS: ["target"],
    }

CMD_MESSAGES = {
        rpl.UNAWAY: "You are no longer marked as being away",
        rpl.WHOISOPERATOR: "Is a server Operator",
        rpl.WHOISIDLE: "seconds idle",
        rpl.ENDOFWHOIS: "end of /WHOIS list",
        err.NOSUCHNICK: "No such nick/channel",
        err.NOSUCHSERVER: "No such server",
        err.NOSUCHCHANNEL: "No such channel",
        err.CANNOTSENDTOCHAN: "Cannot send to channel",
        err.TOOMANYCHANNELS: "You have joined too many channels",
        err.WASNOSUCHNICK: "There was no such nickname",
        err.TOOMANYTARGETS: "Duplicate recipients, No message delivered",
        err.NOORIGIN: "No origin specified",
        err.NORECIPIENT: "No recipient given",
        err.NOTEXTTOSEND: "No text to send",
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
                print(f"Response {response} requires: {[param for param in CMD_PARAMS[response]]} as arguments")
    if response in CMD_MESSAGES:
        params.append(f":{CMD_MESSAGES[response]}")

    return Params(params)

