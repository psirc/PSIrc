# response_params.py
#
# This file defines all error parameters and messages
# A function that returns a Params object is also defined
# the function will ensure that the message is defined properly

from psirc.message import Params
from psirc.defines.responses import Command
import logging

CMD_PARAMS = {
    Command.RPL_AWAY: ["nickname", "trailing"],
    Command.RPL_WHOISUSER: ["nickname", "user", "host", "real_name"],
    Command.RPL_WHOISSERVER: ["nickname", "server", "server_info"],
    Command.RPL_WHOISOPERATOR: ["nickname"],
    Command.RPL_WHOISIDLE: ["nickname", "seconds_idle"],
    Command.RPL_ENDOFWHOIS: ["nickname"],
    Command.RPL_WHOISCHANNELS: ["nickname", "channel"],
    Command.RPL_TOPIC: ["channel", "trailing"],
    Command.RPL_NAMREPLY: ["symbol", "channel", "trailing"],
    Command.RPL_ENDOFNAMES: ["channel"],
    Command.ERR_NOSUCHNICK: ["nickname"],
    Command.ERR_NOSUCHCHANNEL: ["channel"],
    Command.ERR_NOSUCHSERVER: ["server"],
    Command.ERR_CANNOTSENDTOCHAN: ["channel"],
    Command.ERR_TOOMANYCHANNELS: ["channel"],
    Command.ERR_WASNOSUCHNICK: ["nickname"],
    Command.ERR_TOOMANYTARGETS: ["target"],
    Command.ERR_NOTONCHANNEL: ["channel"],
    Command.ERR_CHANOPRIVSNEEDED: ["channel"],
    Command.PASS: ["password"],
    Command.NICK: ["nickname", "[hopcount]"],
    Command.USER: ["username", "hostname", "servername", "realname"],
    Command.PRIVMSG: ["receiver", "trailing"],
    Command.PING: ["receiver"],
    Command.PONG: ["receivedby"],
    Command.JOIN: ["channel"],
    Command.CAP: ["param", "spec"],
    Command.OPER: ["user", "password"],
    Command.CONNECT: ["target_server", "[port]", "[remote_server]"],
    Command.SERVER: ["servername", "hopcount", "trailing"],
    Command.NAMES: ["[channel]"],
    Command.PART: ["channel"],
    Command.KICK: ["channel", "nickname", "trailing"],
}

CMD_MESSAGES = {
    Command.RPL_WELCOME: "Welcome to the server!",
    Command.RPL_UNAWAY: "You are no longer marked as being away",
    Command.RPL_WHOISOPERATOR: "Is a server Operator",
    Command.RPL_WHOISIDLE: "seconds idle",
    Command.RPL_ENDOFWHOIS: "end of /WHOIS list",
    Command.RPL_ENDOFNAMES: "End of /NAMES list",
    Command.RPL_YOUREOPER: "You are now an IRC operator",
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
    Command.ERR_PASSWDMISMATCH: "Password incorrect",
    Command.ERR_NEEDMOREPARAMS: "Not enough parameters",
    Command.ERR_ALREADYREGISTRED: "You may not reregister",
    Command.ERR_NOTONCHANNEL: "You're not on that channel",
    Command.ERR_CHANOPRIVSNEEDED: "You're not channel operator",
    Command.ERR_NOPRIVILEGES: "Permission Denied- You're not an IRC operator",
}


def parametrize(command: Command, *, recepient: str | None = None, **kwargs: str) -> Params | None:
    """
    Get a valid Params object for a given command/reply/error
    """
    params = {}
    if command in CMD_PARAMS:
        # Numeric replies need a recepient
        if command.value < 1000:
            if not recepient:
                logging.warning("Numeric commands require a 'recepient' parameter")
                return None
        # Other parameters
        for param in CMD_PARAMS[command]:
            if param.startswith("[") and param.endswith("]"):
                param_value = kwargs.get(param)
                param = param[1:-1]
                if param_value:
                    params[param] = param_value
            else:
                param_value = kwargs.get(param)
                if param_value:
                    params[param] = param_value
                else:
                    logging.warning(
                        f"Response {command.name} requires: {[param for param in CMD_PARAMS[command]]} as arguments"
                    )
                    return None
    if command in CMD_MESSAGES:
        params["response"] = f":{CMD_MESSAGES[command]}"

    return Params(params, recepient=recepient)
