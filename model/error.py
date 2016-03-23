class ActionError(Exception):
    def __init__(self, error_type, params):
        self.error_type = error_type
        self.params = params

        '''Make message'''
        if self.error_type == "CMD":
            self.message = "Invalid command {}".format(self.params)
        elif self.error_type == "NAME":
            self.message = "Invalid name: {}".format(self.params)
        elif self.error_type == "TEAM":
            self.message = "Invalid Team. You cannot do that action to someone on that team."
        elif self.error_type == "ME":
            self.message = "You are {}".format(params)
        elif self.error_type == "THEM":
            self.message = "Your target is {}".format(params)
        elif self.error_type == "REPLY":
            self.message = "Reply {} is invalid".format(self.params)
        elif self.error_type == "LOCATION":
            self.message = "Your location \"{}\" is invalid".format(self.params)
        elif self.error_type == "ROLE":
            self.message = "You are not the {}".format(self.params)
        elif self.error_type == "TIME":
            self.message = "You cannot set a time {} before current time {}".format(self.params[0], self.params[1])
        elif self.error_type == "BOMB":
            self.message = "You cannot set the bomb at this time. Please wait until midnight."
        elif self.error_type == "INVUL":
            self.message = "You cannot set invul at this time. Please wait until midnight."

    def __str__(self):
        return repr(self.message)
