import logging
from model.util import Util
from model.player import Team, Player
from model.error import ActionError
from model.actions import Action
from datetime import datetime


class Kill(object):
    @staticmethod
    def handler(attacker, params):
        logging.info("KILL start")

        victim = Util.get_victim(params[0])

        Kill.validate_kill(attacker, victim)

        action = Action()
        action.attacker = attacker.key.id()
        action.action = "KILL"
        action.victim = victim.key.id()
        action.datetime = datetime.now()
        action.need_validation = True
        action_key = action.put()

        logging.info("KILL finish")

        return action.victim, "[REPLY {}] {} claimed to have killed you. \
            Reply Y/N.".format(action_key.id(), attacker.realname)

    @staticmethod
    def validate_kill(attacker, victim):
        my_team = Team.get_by_id(attacker.team)
        if not my_team:
            logging.error("KILL: unable to get my team to validate kill")
            raise
        my_target = my_team.kill
        victim_team = Team.get_by_id(victim.team)
        if not victim_team:
            logging.error("KILL: unable to get vicitm team to validate kill")
            raise
        if victim_team.key.id() != my_target:
            logging.debug("KILL: target team != victim team")
            raise ActionError("TEAM", "")

        if attacker.state == "DEAD":
            logging.debug("KILL: I am dead")
            raise ActionError("ME", attacker.state)

        if victim.state != "ALIVE":
            logging.debug("KILL: Victim is not alive")
            raise ActionError("THEM", victim.state)

        if victim.invul:
            logging.debug("KILL: Victim is invul")
            raise ActionError("THEM", "INVUL")

        if attacker.disarm:
            logging.debug("KILL: Attacker is DISARM")
            raise ActionError("ME", "DISARM")

        logging.debug("KILL: kill validated")

    @staticmethod
    def reply_handler(action, response):
        if response == "Y" or response == "y":
            action.need_validation = False
            action.incorrect_kill = False
            action.put()

            victim = Player.get_by_id(action.victim)
            victim.state = "DEAD"
            victim.put()

            return "*", "{} has been killed".format(victim.codename)
        else:
            action.need_validation = False
            action.incorrect_kill = False
            action.put()
            return action.attacker, "Your victim claims that he/she was not killed.\
                Please check that you have the correct codename"

