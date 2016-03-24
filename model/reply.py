from model.actions import Action
from model.player import Player
import logging
from datetime import datetime
from model.kill import Kill
from model.bomb import Bomb
from model.disarm import Disarm
from model.error import *


class Reply(object):
    @staticmethod
    def handler(ref, params, From):
        logging.debug("REPLY {}".format(ref))
        lookup = Action.get_by_id(int(ref))
        if not lookup:
            raise ReplyError("ref num", ref)

        response = params[0]
        if response != "Y" and response != "y" and response != "N" and response != "n":
            raise ReplyError(response, ref)

        if lookup.action == "DISARM":
            return Disarm.reply_handler(lookup, response)
        else:
            # TODO: Add logic for pushing team to next target 
            if lookup.action == "KILL":
                return Kill.reply_handler(lookup, response)
            elif lookup.action == "BOMB":
                return Bomb.reply_handler(lookup, response, From)
        raise ReplyError(response, ref)
