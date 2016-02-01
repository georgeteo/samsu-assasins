from model.actions import Action
from model.player import Player
import logging
from model.error import ActionError
from datetime import datetime


class Reply(object):
    @staticmethod
    def handler(ref, params, From):
        logging.debug("REPLY {}".format(ref))
        lookup = Action.get_by_id(int(ref))
        if not lookup:
            raise ActionError("REPLY", "reference number")

        # Deep copy if bomb
        if lookup.victim == "*":
            lookup2 = Action()
            lookup2.attacker = lookup.attacker
            lookup2.action = lookup.action
            lookup2.victim = From.key.id()
            lookup2.datetime = datetime.now()
            lookup2.place = lookup.place
        else:
            lookup2 = lookup

        response = params[0]
        if response == "Y" or response == "y":
            lookup2.need_validation = False
            lookup2.incorrect_kill = False

            lookup_victim = Player.get_by_id(lookup2.victim)
            lookup_victim.state = "DEAD"
            lookup_victim.put()

            lookup2.put()

            return "*", "{} has been killed".format(lookup_victim.codename)
        elif response == "N" or response == "n":
            lookup2.need_validation = True
            lookup2.incorrect_kill = True
            return lookup2.attacker, "Your victim claims he/she was not killed.\
                Please check that you have the correct codename."
        else:
            raise ActionError("REPLY", "Y/N")
