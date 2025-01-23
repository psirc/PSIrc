import re
from psirc.message import Message, Prefix, Params
from psirc.irc_validator import IRCValidator
from psirc.defines.responses import Command

from psirc.response_params import CMD_PARAMS, parametrize


class MessageParser:
    message_regex = r"^(:(?P<prefix>\S+)\s)?(?P<cmd>\S+)(\s(?P<params>.*?))?(?:\s:(?P<trail>.*))?$"
    prefix_regex = r"^(?P<nick>[^\s!.@]+)(!(?P<user>[^\s@!]+))?(@(?P<host>\S+))?$|^(?P<servername>\S+)$"

    @classmethod
    def _parse_prefix(cls, prefix: str) -> Prefix | None:
        """Parse a command prefix into a Prefix type object

        :param prefix: The prefix string
        :type prefix: ``str``
        :return: A prefix type object if the prefix was valid
        :rtype: ``Prefix`` or ``None``
        """

        match = re.match(cls.prefix_regex, prefix)
        if not match:
            return None

        if sender := match.group("servername"):
            return Prefix(sender) if IRCValidator.validate_host(sender) else None

        nick, user, host = match.group("nick", "user", "host")

        if all(
            (
                IRCValidator.validate_nick(nick),
                host is None or IRCValidator.validate_host(host),
            )
        ):
            return Prefix(nick, user or "", host or "")

    @staticmethod
    def _numeric_command(command: str) -> Command | None:
        """Check if command is a valid numeric command

        :param command: The command to be tested
        :type command: ``str``
        """

        if command.isdigit() and int(command) in Command:
            return Command(int(command))
        return None

    @staticmethod
    def _text_command(command: str) -> Command | None:
        """Check if command is a valid text command

        :param command: The command to be tested
        :type command: ``str``
        """
        if command in Command.__members__:
            return Command.__members__[command]
        return None

    @classmethod
    def _valid_command(cls, command: str) -> Command | None:
        """Check if command is a valid command

        :param command: The command to be tested
        :type command: ``str``
        :return: Command enum object if the command is valid
        :rtype: ``Command`` or ``None``
        """

        numeric_command = cls._numeric_command(command)
        return numeric_command if numeric_command else cls._text_command(command)

    @staticmethod
    def _parse_params(command: Command, params: str, trail: str) -> Params | None:
        """Parse the command params into a valid Params object

        :param command: The command for which the params are parsed
        :type command: ``Command``
        :param params: The string of command parameters
        :type params: ``str``
        :param trail: The trailing of a message
        :type trail: ``str``
        :return: The params type object if the command has parameters
        :rtype: ``Params`` or ``None``
        """

        # command has no params defined
        if command not in CMD_PARAMS.keys():
            return None

        params_list = params.split()
        params_list.append(trail) if trail else None

        params_dict = {CMD_PARAMS[command][i]: param for i, param in enumerate(params_list)}
        return parametrize(command, **params_dict)

    @classmethod
    def parse_message(cls, data: str) -> Message | None:
        print(f"message parse: data: {data}")
        """Parse a received message string

        :param data: The received message
        :type data: ``str``
        :return: a Message type object if the data was valid
        :rtype: ``Message`` or ``None``
        """

        match = re.match(cls.message_regex, data)
        if not match:
            print("Unable to match with message regex")
            return None
        prefix, command, params, trailing = match.group("prefix", "cmd", "params", "trail")
        prefix = cls._parse_prefix(prefix) if prefix else None
        command = cls._valid_command(command)
        if not command:
            return None
        params = cls._parse_params(command, params, trailing)
        return Message(prefix=prefix, command=command, params=params)
