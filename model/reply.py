from model.actions import Action
from model.player import Player
import logging
from model.error import ActionError


class Reply(object):
    @staticmethod
    def handler(ref, params):
        logging.debug("Action Builder: REPLY {}".format(ref))
        lookup = Action.get_by_id(int(ref))
        if not lookup:
            raise ActionError("REPLY", "reference number")
        response = params[0]
        if response == "Y" or response == "y":
            lookup.need_validation = False
            lookup.incorrect_kill = False

            lookup_victim = Player.get_by_id(lookup.victim)
            lookup_victim.state = "DEAD"
            lookup_victim.put()
            lookup.put()

            return "*", "{} has been killed".format(lookup_victim.codename)
        elif response == "N" or response == "n":
            lookup.need_validation = True
            lookup.incorrect_kill = True
            return lookup.attacker, "Your victim claims he/she was not killed.\
                Please check that you have the correct codename."
        else:
            raise ActionError("REPLY", "Y/N")
