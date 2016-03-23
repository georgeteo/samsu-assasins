from datetime import datetime

class ErrorMixin(Exception):
    """ Error Mixin 
    Note: This mixin must be inherited with a constructor that has a message
    attribute. 
    """
    def __str__(self):
        return repr(self.message)

class CommandError(ErrorMixin):
    """ Error: Wrong command """
    def __init__(self, message):
        self.message = "Invalid command: {}".format(message)

class DbError(ErrorMixin):
    """ Error: Db error """
    def __init__(self, message):
        self.message = "Cannot find name in database: {}".format(message)


class TeamError(ErrorMixin):
    """ Error: target team error """
    def __init__(self):
        self.message = "Invalid Team. You cannot do that action to someone on that team."


class MeError(ErrorMixin):
    """ Error: my state is invalid """
    def __init__(self, message):
        self.message = "You are {}".format(message)
        
        
class TargetError(ErrorMixin):
    """ Target state is invalid """
    def __init__(self, message):
        self.message = "Your target is {}".format(message)


class TimeError(ErrorMixin):
    """ Unable to set time 
    Note: Pass in chi datetime object. 
    Datetime -> Str conversion handled here. """
    def __init__(self, tried_to_set, before_time):
        if type(tried_to_set) == datetime:
            self.message = "You cannot set {} before time {}.".\
                format(tried_to_set.strftime("%m-%d %I:%M%p"),\
                before_time.strftime("%m-%d %I:%M%p"))
        else:
            self.message = "You cannot set {} before time {}.".\
                    format(tried_to_set, before_time.strftime("%m-%d %I:%M%p"))


class ReplyError(ErrorMixin):
    """ Reply Error """
    def __init__(self, msg, ref_num):
        self.message = "Reply {} is invalid. Ref num: {}".format(\
                msg, ref_num)
