from model.reply import Reply
from model.kill import Kill
from model.util import Util
from model.error import ActionError
import logging
from model.bomb import Bomb
from model.disarm import Disarm
from model.player import Player

class CommandHandler(object):

    @staticmethod
    def handler(message):
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

    @staticmethod
    def inner_handler(message):
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
        else:
            raise ActionError("CMD", action)

    @staticmethod
    def get_command(body):
        message_body = body.split()
        action = message_body.pop(0)
        params = message_body
        logging.info("Get Command: Parsed {} - {}".format(action, params))
        return action, params
