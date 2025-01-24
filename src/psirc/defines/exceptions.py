class BannedFromChannel(Exception):
    pass


class BadChannelKey(Exception):
    pass


class NoSuchChannel(Exception):
    pass


class NotOnChannel(Exception):
    pass


class ChanopPrivIsNeeded(Exception):
    pass


class NoSuchNick(Exception):
    pass


class NickAlreadyInUse(Exception):
    pass
