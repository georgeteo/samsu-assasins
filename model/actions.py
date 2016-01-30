from google.appengine.ext import ndb
from player import Player
from datetime import datetime
from error import ActionError
import logging


class Action(ndb.Model):
    '''
    Action object
    Key: default assigned by NDB
    Fields:
        attacker - phone number
        action - string
        victim - phone number
        datetime
        place
        validation
    '''
    attacker = ndb.StringProperty(required=True)
    action = ndb.StringProperty(required=True,
                                choices=set(["KILL",
                                             "DISARM",
                                             "INVUL",
                                             "SNIPE",
                                             "BOMB"]))
    victim = ndb.StringProperty(default="")
    datetime = ndb.DateTimeProperty(required=True)
    place = ndb.StringProperty(default="")
    need_validation = ndb.BooleanProperty(default=True)


class ActionBuilder(object):
    '''Action builder which takes a message object and returns ActionObject.'''
    action = Action()

    def __init__(self, message):
        logging.debug("Action Builder Message: %s, %s, %s".format(message.From, message.To, message.Body))
        self.message = message

    def make_action(self):
        action, params = self._get_command()
        log.debug("Action Builder Action: %s, %s, %s".format(action.attacker, action.action, action.victim))
        self._get_attacker()

        if action == "KILL":
            return self._kill(params), self.action()
        elif action[1:] == "REPLY":
            ref = params.pop(0)
            return self._reply(ref, params)
        else:
            raise ActionError("CMD", action)

    def _get_command(self):
        message_body = self.message.Body.split()
        action = message_body.pop(0)
        params = message_body
        return action, params

    def _get_attacker(self):
        self.attacker = Player.get_by_id(self.message.From)
        log.debug("Action Builder Attacker: %s)".format(self.attacker.realname))

    def _get_victim(self, victim_name):
        potential_victims = Player.query(Player.codename == victim_name).fetch()
        for i, victim in enumerate(potential_victims):
            if i > 0:
                raise ActionError("NAME", victim_name)
            self.victim = victim
            log.debug("Action Builder Attacker: %s)".format(self.victim.realname))
        raise ActionError("NAME", victim_name)

    def _kill(self, params):
        victim = params[0]
        self._get_victim(victim)
        if self._validate_kill():
            ''' Invalid kill '''
            return
        self.action.attacker = self.attacker.key.id()
        self.action.action = "KILL"
        self.action.victim = self.victim.id()
        self.action.datetime = datetime.now()
        self.action.need_validation = True
        return self.action.put()

    def _validate_kill(self):
        my_teamname = self.attacker.team
        my_team = Team.get_by_id(my_teamanme)
        my_target = my_team.kill
        victim_teamname = self.victim.team
        victim_team = Team.get_by_id(victim_teamanme)
        if my_target != victim_team.id():
            raise ActionError("TEAM", "")

        if self.attacker.state == "DEAD":
            raise ActionError("ME", self.attacker.state)

        if self.victim.state != "ALIVE":
            raise ActionError("THEM", self.victim.state)

        return False

    def _reply(self, ref, params):
        lookup = Action.get_by_id(ref)
        if not lookup:
            raise ActionError("REPLY", "reference number")
        # TODO: add more validation here (on KILL, victims match)
        response = params[0]
        if response == "Y" or response == "y":
            lookup.need_validation = False
            return lookup.put(), lookup
        else:
            raise ActionError("REPLY", "Y/N")
