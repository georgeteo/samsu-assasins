from flask import Flask, request
from twilio.rest import TwilioRestClient
from model.handler import CommandHandler
from model.message import Message
from model.error import ActionError
from model.player import Player
from model.actions import Action
from model.bomb import Bomb
import logging
from datetime import datetime
from model.util import Util
import pytz

app = Flask(__name__)

ACCOUNT_SID = "AC04675359e5f5e5ca433a2a5c17e9ddf6"
AUTH_TOKEN = "ea3bc3ef80b8a7283d26eb94426518c8"
SERVER_NUMBER = "+13126989087"
WEI_HAN = "+13127310539"

@app.route('/')
def index():
    return "Welcome to SAMSU assassins. The site is up and working.\
        Have a nice day."

@app.route('/twil', methods=['POST'])
def twil():
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    from_ = request.form.get("From", WEI_HAN)
    body = request.form.get("Body", default="")
    picture = request.form.get("Picture", default="")
    message_id = request.form.get("MessageSid", default="")

    log = "IN: MessageSid = {}, From = {}, Body = {}".format(message_id, from_, body)
    logging.info(log)

    message = Message(From=from_,
                      To=SERVER_NUMBER,
                      Body=body,
                      Picture=picture,
                      id=message_id)
    message.put()

    ''' Pass message into action builder.'''
    try:
        response_to, response = CommandHandler.handler(message)
        if response_to == "*":
            response_num_list = [key.id() for key in Player.query().fetch(keys_only=True)]
        else:
            response_num_list = [response_to]

    except ActionError as message:
        logging.exception("Error {}".format(message))
        response_num_list = [from_]
        response = "[ERR] {}".format(message)
    except:
        logging.exception("Unknown Error")
        response_num_list = [from_]
        response = "[ERR] Unknown Error"

    for response_number in response_num_list:
        logging.info("Making message {} for {} with num_lis {}".format(response, response_number, response_num_list))

        '''Make message'''
        outgoing_message = Message(From=SERVER_NUMBER,
                                   To=response_number,
                                   Body=response)
        outgoing_message.put()

        '''Send message'''
        client.messages.create(
            to=response_number,
            from_=SERVER_NUMBER,
            body=response)

    return log

@app.route('/bomb', methods=['POST'])
def bomb_worker():
    ''' Get bomb id '''
    req_key = request.form.get('id', "")
    bomb = Bomb.get_by_id(int(req_key))

    ''' ERROR: no bomb found by id '''
    if not bomb:
        logging.error("BOMB Worker: No bomb found by key {}".format(req_key))
        raise Exception()

    ''' Bomb deprecated no action '''
    if bomb.deprecated:
        logging.info("BOMB Worker: Bomb with key {} deprecated. No explosion".format(req_key))
        return

    ''' Trigger bomb '''
    logging.info("BOMB: triggered at {} UTC {} Chicago".format(
        datetime.now(),
        Util.utc_to_chi(datetime.now().replace(tzinfo=pytz.utc))))
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    attacker = Player.get_by_id(bomb.attacker)
    attacker.can_set_bomb_after = Util.next_day()
    attacker.put()

    bomb.trigger = True
    bomb_key = bomb.put()

    action = Action()
    action.attacker = bomb.attacker
    action.action = "BOMB"
    action.victim = "*"
    action.datetime = datetime.now()
    action.place = bomb.place
    action_key = action.put()

    response_num_list = [key.id() for key in Player.query(Player.state.IN(["ALIVE", "DISARM"]) ).fetch(keys_only=True)]
    response = "[REPLY {}] {} has been bombed at {}. Reply Y if you were there.".format(
        action_key.id(), action.place,
        Util.utc_to_chi(action.datetime.replace(tzinfo=pytz.utc)).isoformat(' '))

    for response_number in response_num_list:
        logging.info("Making message {} for {} with num_list {}".format(
            response, response_number, response_num_list))

        '''Make message'''
        outgoing_message = Message(From=SERVER_NUMBER,
                                   To=response_number,
                                   Body=response)
        outgoing_message.put()

        '''Send message'''
        client.messages.create(
            to=response_number,
            from_=SERVER_NUMBER,
            body=response)

    return "Bomb triggered at {}".format(bomb.place)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e),z500
