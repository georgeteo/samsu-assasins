from google.appengine.ext import ndb
from model.error import *
from google.appengine.api import taskqueue
from datetime import datetime, timedelta
import logging
from model.util import Util
from model.actions import Action
import pytz
from model.player import Player
import re

class Invul(ndb.Model):
    """ INVUL <target codename> <month> <day> <hour> <min> """

    medic = ndb.StringProperty()
    target = ndb.StringProperty()
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty()
    in_effect = ndb.BooleanProperty(default=False)
    deprecated = ndb.BooleanProperty(default=False)

    @classmethod
    def handler(cls, attacker, params):
        """ Validation """
        if len(params) != 5:
            raise CommandError("INVUL - {}".format(params))

        if attacker.state == "DEAD":
            raise MeError("DEAD")
        
        if attacker.role != "MEDIC":
            raise MeError("not MEDIC")

        target_codename = params.pop(0)
        target = Util.get_victim(target_codename)

        if target.team != attacker.team:
            raise TeamError

        if target.state == "DEAD":
            raise TargetError("DEAD")

        chi_start_time = datetime(year=2016, month=int(params[0]),\
                day=int(params[1]), hour=int(params[2]),\
                minute=int(params[3]))
        utc_start_time = Util.chi_to_utc(chi_start_time)
        utc_end_time = utc_start_time + timedelta(hours=1)

        if utc_start_time < datetime.now():
            raise TimeError(chi_start_time, Util.utc_to_chi(datetime.now()))

        if datetime.now() < attacker.can_set_after:
            raise TimeError("invul", Util.utc_to_chi(attacker.can_set_after))

        """ Make new Invul """
        invul = Invul()
        invul.medic = attacker.key.id()
        invul.target = target.key.id()
        invul.start_time = utc_start_time
        invul.end_time = utc_end_time

        """ Invalidate old invul """
        try:
            old_invul = Invul.get_by_id(attacker.item)
            logging.info("INVUL: invalidating old invul with id {}".\
                    format(attacker.item))
            if old_invul.in_effect or old_invul.deprecated:
                raise TimeError("invul" "midnight")
            old_invul.deprecated = True
            old_invul.put()
        except:
            logging.info("INVUL: unable to invalidate old invul")

        invul_key = invul.put()
        attacker.item = invul_key.id()
        attacker.put()

        task = taskqueue.Task(url="/invul", params={"id": invul_key.id()},\
                eta = utc_start_time)
        task.add(queue_name="invul")

        return [(invul.medic, "Invul will been set for {} from {} to {}.".\
                format(target_codename,\
                chi_start_time.strftime("%m-%d %I:%M%p"),
                Util.utc_to_chi(utc_end_time).strftime("%m-%d %I:%M%p")))]


        

        
        



    

    
