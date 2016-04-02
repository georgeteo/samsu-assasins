import logging
from model.util import Util
from model.player import Team, Player
from model.error import *
from model.actions import Action
from datetime import datetime


class Kill(object):
    """
    KILL <codename>
    """

    @classmethod
    def handler(cls, attacker, params):
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

        return [(action.victim, "[REPLY {}] {} claimed to have killed you. " 
            "Reply Y/N.".format(action_key.id(), attacker.realname))]

    @classmethod
    def validate_kill(cls, attacker, victim):
        my_team = Team.get_by_id(attacker.team)
        if not my_team:
            logging.error("KILL: unable to get my team {} to validate kill"\
                    .format(attacker.team))
            raise
        my_target = my_team.to_kill
        victim_team = Team.get_by_id(victim.team)
        if not victim_team:
            logging.error("KILL: unable to get vicitm team to validate kill")
            raise

        if victim_team.key.id() != my_target:
            logging.debug("KILL: target team {} != victim team {}".format(victim_team.key.id(), my_target))
            raise TeamError

        if attacker.state == "DEAD":
            logging.debug("KILL: Attacker is DEAD")
            raise MeError(attacker.state)

        if victim.state != "ALIVE":
            logging.debug("KILL: Victim is DEAD")
            raise TargetError(victim.state)

        if victim.invul:
            logging.debug("KILL: Victim is INVUL")
            raise TargetError("INVUL")

        if attacker.disarm:
            logging.debug("KILL: Attacker is DISARM")
            raise MeError("DISARM")

        logging.info("KILL: kill validated")

    @classmethod
    def reply_handler(cls, action, response):
        if response == "Y" or response == "y":
            action.need_validation = False
            action.incorrect_kill = False
            action_key = action.put()

            victim = Player.get_by_id(action.victim)
            victim.state = "DEAD"
            victim.killed_by = action_key.key.id()
            victim.put()

            attacker = Player.get_by_id(action.attacker)
            attacker.killed.append(victim.realname)
            attacker.put()



            return [("*", "{} has been killed".format(victim.codename))]
        else:
            action.need_validation = False
            action.incorrect_kill = False
            action.put()
            return [(action.attacker, "Your victim claims that he/she was not "
            "killed. Please check that you have the correct codename")]
