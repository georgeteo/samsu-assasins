from model.util import Util
from model.error import *
from model.player import Player, Team
from model.actions import Action

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from datetime import datetime, timedelta
import logging

class Disarm(ndb.Model):
    """ DISARM <codename> """

    attacker = ndb.StringProperty()
    victim = ndb.StringProperty()
    startime = ndb.DateTimeProperty()
    endtime = ndb.DateTimeProperty()
    deprecated = ndb.BooleanProperty(default=False)

    @classmethod
    def handler(cls, attacker, params):

        if len(params) == 0:
            raise CommandError("Parameter {}".format(params))

        victim = Util.get_victim(params[0])
        Disarm.validate_disarm(attacker, victim)

        action = Action()
        action.attacker = attacker.key.id()
        action.action = "DISARM"
        action.victim = victim.key.id()
        action.datetime = datetime.now()
        action.need_validation = True
        action_key = action.put()

        return [(action.victim, "{} claimed to have disarm you. "
            "[REPLY {}] Y/N.".format(attacker.realname, action_key.id()))]

    @classmethod
    def reply_handler(cls, action, response):
        if response == "Y" or response == "y":
            action.need_validation = False
            action.incorrect_kill = False
            action_key = action.put()

            victim = Player.get_by_id(action.victim)
            victim.disarm = True
            victim.put()

            disarm = Disarm()
            disarm.attacker = action.attacker
            disarm.victim = action.victim
            disarm.starttime = datetime.now()
            disarm.endtime = datetime.now() + timedelta(hours = 1)
            disarm_key = disarm.put()

            task = taskqueue.Task(url="/disarm", params={"id": disarm_key.id()},
                    eta=disarm.endtime)
            task.add(queue_name="disarm")
            q = taskqueue.Queue('disarm').fetch_statistics()
            logging.critical(q)

            return [(action.victim, "You have been DISARM until {}".format(\
                    Util.utc_to_chi(disarm.endtime).strftime("%m-%d %I:%M%p")))]
        else:
            action.need_validation = False
            action.incorrect_kill = False
            action.put()
            return [(action.attacker, "Your DISARM target claims he was not "
                "disarmed by you.")]

    @classmethod
    def validate_disarm(cls, attacker, victim):
        my_team = Team.get_by_id(attacker.team)
        if not my_team:
            logging.error("DISARM: unable to get my team {} to validate kill"\
                    .format(attacker.team))
            raise
        my_target = my_team.target_of
        victim_team = Team.get_by_id(victim.team)
        if not victim_team:
            logging.error("DISARM: unable to get vicitm team to validate kill")
            raise

        if victim_team.key.id() != my_target:
            logging.debug("DISARM: target team != victim team")
            raise TeamError

        if attacker.state == "DEAD":
            logging.debug("DISARM: Attacker is DEAD")
            raise MeError(attacker.state)

        if victim.state == "DEAD":
            logging.debug("DISARM: Victim is DEAD")
            raise TargetError(victim.state)
