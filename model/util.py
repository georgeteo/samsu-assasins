from model.player import Player
import logging
from model.error import ActionError

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
