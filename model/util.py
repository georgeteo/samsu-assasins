from model.player import Player
import logging
from model.error import DbError
import pytz
from datetime import datetime, timedelta, date, time

class Util(object):
    @classmethod
    def get_attacker(cls, attacker_number):
        attacker = Player.get_by_id(attacker_number)
        if not attacker:
            logging.error("Get Attacker: attacker number {} not found in \
                          get_attacker()".format(attacker_number))
            raise
        logging.info("Get Attacker: attacker {} found".format(
            attacker.realname))
        return attacker

    @classmethod
    def get_victim(cls, victim_name):
        victim = Player.query(Player.codename == victim_name).get()
        if not victim:
            logging.error("Get Victim: victim {} not found".format(victim_name))
            logging.error("Database looks like: {}".format(Player.query().fetch()))
            raise DbError(victim_name)
        logging.info("Get Victim: victim {} found".format(victim_name))
        return victim

    @classmethod
    def chi_to_utc(cls, chi_dt):
        return chi_dt.replace(tzinfo=None) + timedelta(hours=6)

    @classmethod
    def utc_to_chi(cls, utc_dt):
        return utc_dt.replace(tzinfo=None) - timedelta(hours=6)

    @classmethod
    def next_day(cls):
        """ Return UTC time """
        chi_today = Util.utc_to_chi(datetime.utcnow()).date()
        chi_tomorrow = chi_today + timedelta(1)
        return datetime.combine(chi_tomorrow, time(6, 0, 0))

