from google.appengine.ext import ndb
from player import Player, Team
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

    @staticmethod
    def make_action(message):
        action, params = ActionBuilder.get_command(message.Body)
        attacker = ActionBuilder.get_attacker(message.From)

        if action == "KILL":
            return ActionBuilder.kill(attacker, params)
        elif action[1:] == "REPLY":
            ref = params.pop(0)
            return self._reply(ref, params)
        else:
            raise ActionError("CMD", action)

    @staticmethod
    def get_command(body):
        message_body = body.split()
        action = message_body.pop(0)
        params = message_body
        logging.info("Action Builder: Parsed {} - {}".format(action, params))
        return action, params

    @staticmethod
    def get_attacker(attacker_number):
        attacker = Player.get_by_id(attacker_number)
        if not attacker:
            logging.error("Action Builder: attacker number {} not found in \
                          get_attacker()".format(attacker_number))
            raise
        logging.info("Action Builder: attacker {} found".format(
            attacker.realname))
        return attacker

    @staticmethod
    def get_victim(victim_name):
        victim = Player.query(Player.codename == victim_name).get()
        if not victim:
            logging.error("Action Builder: victim {} not found".format(victim_name))
            raise ActionError("NAME", victim_name)
        logging.info("Action Builder: victim {} found".format(victim_name))
        return victim

    @staticmethod
    def kill(attacker, params):
        logging.info("Action Builder: KILL start")

        victim = ActionBuilder.get_victim(params[0])

        ActionBuilder.validate_kill(attacker, victim)

        action = Action()
        action.attacker = attacker.key.id()
        action.action = "KILL"
        action.victim = victim.key.id()
        action.datetime = datetime.now()
        action.need_validation = True

        logging.info("Action Builder: KILL finish")

        return action.put(), action

    @staticmethod
    def validate_kill(attacker, victim):
        my_team = Team.get_by_id(attacker.team)
        if not my_team:
            logging.error("Action Builder: unable to get my team to validate kill")
            raise
        my_target = my_team.kill
        victim_team = Team.get_by_id(victim.team)
        if not victim_team:
            logging.error("Action Builder: unable to get vicitm team to validate kill")
            raise
        if victim_team.key.id() != my_target:
            logging.debug("Action Builder: target team != victim team")
            raise ActionError("TEAM", "")

        if attacker.state == "DEAD":
            logging.debug("Action Builder: I am dead")
            raise ActionError("ME", self.attacker.state)

        if victim.state != "ALIVE":
            logging.debug("Action Builder: Victim is not alive")
            raise ActionError("THEM", self.victim.state)

        logging.debug("Action Builder: kill validated")

    def _reply(self, ref, params):
        logging.debug("Action Builder: REPLY")
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
