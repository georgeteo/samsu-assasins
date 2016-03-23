from google.appengine.ext import ndb
from model.error import *
from google.appengine.api import taskqueue
from datetime import datetime
import logging
from model.util import Util
from model.actions import Action
import pytz
from model.player import Player
import re

class Bomb(ndb.Model):
    """
    BOMB <location> <month> <date> <hour> <min>
    DEMO is allowed to reset a bomb as long as it has not yet exploded.
    """
    
    attacker = ndb.StringProperty()
    place = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    trigger = ndb.BooleanProperty(default=False)
    deprecated = ndb.BooleanProperty(default=False)

    @staticmethod
    def handler(attacker, params):
        '''Validation'''
        if attacker.state == "DEAD":
            raise MeError("DEAD")

        if attacker.role != "DEMO":
            raise MeError("not DEMO")

        if datetime.now() < attacker.can_set_after:
            raise TimeError("bomb", Util.utc_to_chi(attacker.can_set_after))

        if attacker.disarm:
            raise MeError("DISARM")

        ''' Parse place and time '''
        if re.match(r"\w \d+ \d+ \d+ \d+", " ".join(params)):
            raise CommandError("BOMB - ".format(" ".join(params)))
        place = params.pop(0)

        central = pytz.timezone("US/Central")
        chi_dt = datetime(2016,
                        int(params[0]),
                        int(params[1]),
                        int(params[2]),
                        int(params[3]),
                        tzinfo=central)
        utc_dt = Util.chi_to_utc(chi_dt)
        logging.debug("CHI time: {}".format(chi_dt))
        logging.debug("UTC time: {}".format(utc_dt))

        if utc_dt < datetime.now():
            cur_time = Util.utc_to_chi(datetime.now())
            logging.error("BOMB: trying to set time {} before now {} (UTC)".format(utc_dt.isoformat(' '), datetime.now().isoformat(' ')))
            raise TimeError(chi_dt, cur_time)

        '''Make new bomb'''
        bomb = Bomb()
        bomb.attacker = attacker.key.id()
        bomb.place = place
        bomb.time = utc_dt
        bomb.trigger = False
        bomb_key = bomb.put()

        ''' Invalidate old bomb '''
        try:
            old_bomb = Bomb.get_by_id(attacker.item)
            logging.info("BOMB: invalidating old bomb with id {}".format(attacker.item))
            old_bomb.deprecated = True
            old_bomb.put()
        except:
            logging.info("BOMB: unable to invalidate old bomb")

        ''' Setting new bomb '''
        attacker.item = bomb_key.id()
        attacker.put()

        task = taskqueue.Task(url="/bomb", params={"id": bomb_key.id()}, eta=utc_dt)
        task.add(queue_name="bomb")

        logging.info("BOMB: set for {} at {}".format(utc_dt, place))

        return [(bomb.attacker, "Your bomb in {} will explode at {}".format(
            bomb.place, chi_dt.strftime("%m-%d %I:%M%p")))]

    @staticmethod
    def reply_handler(action, response, from_):
        # Deep copy bomb
        action_c = Action()
        action_c.attacker = action.attacker
        action_c.action = action.action
        action_c.victim = from_.key.id()
        action_c.datetime = datetime.now()
        action_c.place = action.place

        if response == "Y" or response == "y":
            action_c.need_validation = False
            action_c.incorrect_kill = False
            action_c.put()

            victim = Player.get_by_id(action_c.victim)
            victim.state = "DEAD"
            victim.put()

            return [("*", "{} has been killed".format(victim.codename))]

        else:
            action_c.need_validation = True
            action_c.incorrect_kill = True
            return []

