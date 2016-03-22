from model.actions import Action
from model.player import Player
import logging
from model.error import ActionError
from datetime import datetime
from model.kill import Kill
from model.bomb import Bomb
from model.disarm import Disarm


class Reply(object):
    @staticmethod
    def handler(ref, params, From):
        logging.debug("REPLY {}".format(ref))
        lookup = Action.get_by_id(int(ref))
        if not lookup:
            raise ActionError("REPLY", "reference number")

        response = params[0]
        if response != "Y" and response != "y" and response != "N" and response != "n":
            raise ActionError("REPLY", response)


        if lookup.action == "DISARM":
            return Disarm.reply_handler(lookup, response)
        else:
            if lookup.action == "KILL":
                return Kill.reply_handler(lookup, response)
            elif lookup.action == "BOMB":
                return Bomb.reply_handler(lookup, response, From)
        raise ActionError("REPLY", response)
