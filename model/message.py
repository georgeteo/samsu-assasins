from google.appengine.ext import ndb
from model.player import Player
import logging


class Message(ndb.Model):
    '''
    Message object.
    Key: TwilMessageid
    Fields:
        From phone number
        To Phone number
        Body raw message body
        Picture image string
    '''
    From = ndb.StringProperty()
    To = ndb.StringProperty()
    Body = ndb.StringProperty()
    Picture = ndb.StringProperty(default="")


class ResponseBuilder(object):

    @staticmethod
    def build_response(action_key, action):
        logging.info("Build Response")
        command = action.action
        if command == "KILL":
            return ResponseBuilder.kill(action_key, action)

    @staticmethod
    def kill(action_key, action):
        logging.info("Building kill response")
        if action.need_validation:
            response_number = [action.victim]
            response = "[REPLY {}] Were you recently killed? Reply 'Y' or 'N'."\
                .format(action_key.id())
        else:
            all_numbers = [key.id() for key in Player.query().fetch(keys_only=True)]
            response_number = [all_numbers]
            victim = Player.get_by_id(action.victim)
            if not victim:
                raise ActionError("REPLY", "Victim Error")
            response = "{} has been killed".format(victim.codename)
        return response_number, response
