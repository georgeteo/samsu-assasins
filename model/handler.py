from model.reply import Reply
from model.kill import Kill
from model.util import Util
from model.error import ActionError
import logging


class CommandHandler(object):

    @staticmethod
    def handler(message):
        action, params = CommandHandler.get_command(message.Body)
        attacker = Util.get_attacker(message.From)

        if action == "KILL":
            return Kill.handler(attacker, params)
        elif action[1:] == "REPLY":
            ref = params.pop(0)[:-1]
            return Reply.handler(ref, params)
        else:
            raise ActionError("CMD", action)

    @staticmethod
    def get_command(body):
        message_body = body.split()
        action = message_body.pop(0)
        params = message_body
        logging.info("Get Command: Parsed {} - {}".format(action, params))
        return action, params
