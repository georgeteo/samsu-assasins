from model.reply import Reply
from model.kill import Kill
from model.util import Util
from model.error import CommandError
import logging
from model.bomb import Bomb
from model.disarm import Disarm
from model.player import Player
from model.snipe import Snipe
from model.invul import Invul

WEI_HAN = "+13127310539"

class CommandHandler(object):

    @classmethod
    def handler(cls, message):
        responses = CommandHandler.inner_handler(message)
        output_responses = []
        for (response_to, response) in responses:
            if response_to == "" and response == "":
                break
            if response_to == "*":
                response_num_list = [key.id() for key in Player.query().fetch(keys_only=True)]
            else:
                response_num_list = [response_to]
            output_responses.append((response_num_list, response))
        return output_responses

    @classmethod
    def inner_handler(cls, message):
        """ Return [(number, msg),...]"""
        action, params = CommandHandler.get_command(message.Body)
        attacker = Util.get_attacker(message.From)

        if action == "KILL":
            return Kill.handler(attacker, params)
        elif action[1:] == "REPLY":
            ref = params.pop(0)[:-1]
            return Reply.handler(ref, params, attacker)
        elif action == "BOMB":
            return Bomb.handler(attacker, params)
        elif action == "INVUL":
            return Invul.handler(attacker, params)
        elif action == "DISARM":
            return Disarm.handler(attacker, params)
        elif action == "SNIPE":
            if message.From != WEI_HAN:
                raise CommandError(action)
            sniper = Player.query(Player.codename == params[0]).get()
            if sniper == None:
                raise DbError(params[0])
            return Snipe.handler(sniper, params[1])
        elif action == "?":
            msg = "Guide for SAMSU Assassins:\n"
            msg += "KILL <target codename>\n"
            msg += "BOMB <place> <mm> <dd> <hour> <min>\n"
            msg += "INVUL <target codename> <mm> <dd> <hour> <min>\n"
            msg += "DISARM <target codename>\n"
            msg += "SNIPE - send message and picture to {}\n".format(WEI_HAN)
            msg += "REPLY - [REPLY <number>] Y or [REPLY <number>] N"
            return [(attacker.key.id(), msg)]
        else:
            raise CommandError(action)

    @classmethod
    def get_command(cls, body):
        message_body = body.split()
        action = message_body.pop(0)
        params = message_body
        logging.info("Get Command: Parsed {} - {}".format(action, params))
        return action, params
