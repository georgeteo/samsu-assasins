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
from google.appengine.api import taskqueue
from model.disarm import Disarm

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
        response_list = CommandHandler.handler(message)
    except ActionError as message:
        logging.exception("Error {}".format(message))
        response_num_list = [from_]
        response = "[ERR] {}".format(message)
    except:
        logging.exception("Unknown Error")
        response_num_list = [from_]
        response = "[ERR] Unknown Error"

    for response_num_list, response in response_list:
        for response_number in response_num_list:
            logging.info("Making message {} for {} with num_list {}".format(response, response_number, response_num_list))

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
        return "BOMB Worker: Deprecated Bomb"

    ''' Trigger bomb '''
    logging.info("BOMB: triggered at {} UTC {} Chicago".format(
        datetime.now(),
        Util.utc_to_chi(datetime.now().replace(tzinfo=pytz.utc))))
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    attacker = Player.get_by_id(bomb.attacker)
    attacker.can_set_after = Util.next_day()
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

@app.route('/invul', methods=["POST"])
def invul_worker():
    ''' Get invul id'''
    req_key = request.form("id", "")
    inv = Invul.get_by_id(int(req_key))

    ''' No Inv found '''
    if not inv:
        logging.error("INV worker: no INV found")
        raise Exception()

    '''Inv deprecated'''
    if inv.deprecated:
        logging.info("INV Worker: Inv deprecated. No action.")
        return "INVUL Worker: Deprecated"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    '''Target dead. Report back to medic'''
    target_num = inv.target
    target = Player.get_by_id(target_num)
    if not target:
        logging.error("INV worker: cannot find target {}".format(target_num))
        return
    if target.state == "DEAD":
        logging.error("INV worker: Target {} has died. Cannot grant INVUL".format(target.codename))
        response = "Your INVUL target has died. Cannot grant dead people INVUL."
        msg = Message(From=SERVER_NUMBER,
                      To=inv.medic,
                      Body=response)
        msg.put()
        client.messages.create(
            to=inv.medic,
            from_=SERVER_NUMBER,
            body=response)
        return "INVUL Worker"

    '''Target alive. If INVUL not yet in effect, trigger'''
    if not inv.in_effect:
        logging.info("INVUL worker: Triggering 1 hour INVUL for target {} at {}".format(target.codename, datetime.now()))
        inv.in_effect = True
        inv_key = inv.put()
        task = taskqueue.Task(url="/invul", params={"id": inv_key.id()}, eta=inv.end_time)
        task.add(queue_name="invul")

        target.invul = True
        target.put()

        response  = "You have been granted INVUL for 1 hour from {} to {}".format(
            inv.start_time, inv.end_time)
        msg = Message(From=SERVER_NUMBER,
                      To=inv.target,
                      Body=response)
        msg.put()
        client.messages.create(
            to=inv.target,
            from_=SERVER_NUMBER,
            body=response)
        return "INVUL Worker"
    else:
        logging.info("INVUL worker: END 1 hour INVUL for target {} at {}".format(target.codename, datetime.now()))
        inv.deprecated = True
        inv.put()
        target.invul = False
        target.put()

        response = "Your INVUL period has ended. You are no longer INVUL."
        msg = Message(From=SERVER_NUMBER,
                      To=inv.target,
                      Body=response)
        msg.put()
        client.messages.create(
            to=inv.target,
            from_=SERVER_NUMBER,
            body=response)
        return "INVUL Worker"

@app.route('/disarm', methods=['POST'])
def disarm_worker():
    ''' Get disarm id'''
    req_key = request.form("id", "")
    disarm = Disarm.get_by_id(int(req_key))

    ''' No disarm found '''
    if not disarm:
        logging.error("DISARM worker: no DISARM found")
        raise Exception()

    '''Disarm deprecated'''
    if disarm.deprecated:
        logging.info("DISARM Worker: Disarm deprecated. No action.")
        return "DISARM Worker: deprecated"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    disarmed_player = Player.get_by_id(disarm.disarmed)
    disarmed_player.disarm = False
    disarm_player.put()

    disarm.deprecated = True
    disarm.put()

    logging.info("DISARM Worker: Turning off disarmed state for {}".format(disarm.disarmed))

    response = "You are no longer DISARMED. Go ahead and kill people."
    msg = Message(From=SERVER_NUMBER,
                  To=disarm.disarmed,
                  Body=response)
    msg.put()
    client.messages.create(
        to=disarm.disarmed,
        from_=SERVER_NUMBER,
        body=response)
    return "DISARM WORKER"


@app.route("/revive")
def revive():
    players = Player.query().fetch()
    for player in players:
        player.state = "ALIVE"
        player.put()
    return "All players revived"





@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e),z500
