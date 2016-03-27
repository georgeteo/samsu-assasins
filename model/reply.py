from model.actions import Action
from model.player import Player, Team
import logging
from datetime import datetime
from model.kill import Kill
from model.bomb import Bomb
from model.disarm import Disarm
from model.error import *


class Reply(object):
    @classmethod
    def handler(cls, ref, params, From):
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
            output_msg = []
            if lookup.action == "KILL":
                output_msg += Kill.reply_handler(lookup, response)
            elif lookup.action == "BOMB":
                output_msg += Bomb.reply_handler(lookup, response, From)
            """ Generate push if necessary """
            output_msg += Team.push(Team.get_by_id(From.team))
            return output_msg
        raise ReplyError(response, ref)
