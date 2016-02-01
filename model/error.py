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
            self.message = "Invalid Team"
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


    def __str__(self):
        return repr(self.message)

