from model.player import Player
import logging
from model.error import ActionError
import pytz
from datetime import datetime, timedelta, date

class Util(object):
    @staticmethod
    def get_attacker(attacker_number):
        attacker = Player.get_by_id(attacker_number)
        if not attacker:
            logging.error("Get Attacker: attacker number {} not found in \
                          get_attacker()".format(attacker_number))
            raise
        logging.info("Get Attacker: attacker {} found".format(
            attacker.realname))
        return attacker

    @staticmethod
    def get_victim(victim_name):
        victim = Player.query(Player.codename == victim_name).get()
        if not victim:
            logging.error("Get Victim: victim {} not found".format(victim_name))
            raise ActionError("NAME", victim_name)
        logging.info("Get Victim: victim {} found".format(victim_name))
        return victim

    @staticmethod
    def chi_to_utc(chi_dt):
        return chi_dt.astimezone(pytz.utc) + timedelta(minutes=7)

    @staticmethod
    def utc_to_chi(utc_dt):
        central = pytz.timezone("US/Central")
        return utc_dt.astimezone(central)

    @staticmethod
    def next_day():
        return datetime.combine(date.today() + timedelta(1), datetime.min.time())
