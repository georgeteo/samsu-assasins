from flask import Flask, request, render_template
from google.appengine.ext import ndb
from twilio.rest import TwilioRestClient
from model.handler import CommandHandler
from model.message import Message
from model.error import *
from model.player import Player, Team
from model.actions import Action
from model.bomb import Bomb
import logging
from datetime import datetime, timedelta
from model.util import Util
import pytz
from google.appengine.api import taskqueue
from model.disarm import Disarm
from forms import PlayerForm, TeamForm
from flask_wtf.csrf import CsrfProtect
from flask_material import Material
from random import shuffle
from model.invul import Invul


app = Flask(__name__)
Material(app)
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

ACCOUNT_SID = "AC04675359e5f5e5ca433a2a5c17e9ddf6"
AUTH_TOKEN = "ea3bc3ef80b8a7283d26eb94426518c8"
SERVER_NUMBER = "+17735701611"
WEI_HAN = "+13127310539"

@app.route('/')
def index():
    return "Samsu assassins is working."

@app.route('/twil', methods=['GET', 'POST'])
def twil():
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    from_ = request.form.get("From", WEI_HAN)
    body = request.form.get("Body", default="")
    picture = request.form.get("MediaUrl{1}", default="")
    message_id = request.form.get("MessageSid", default="")

    log = "IN: MessageSid = {}, From = {}, Body = {}".format(message_id, from_, body)
    logging.info(log)

    message = Message(From=from_,
                      To=SERVER_NUMBER,
                      Body=body,
                      id=message_id)
    message.put()

    ''' Pass message into action builder.'''
    response_list = []
    try:
        response_list = CommandHandler.handler(message)
    except (CommandError, DbError, TeamError, MeError, TargetError, TimeError,\
            ReplyError) as message:
        logging.exception("Error {}".format(message.message))
        response_num_list = [from_]
        response = "[ERR] {}".format(message.message)
        response_list = [(response_num_list, response)]
    except:
        logging.exception("Unknown Error")
        response_num_list = [from_]
        response = "[ERR] Unknown Error"
        response_list = [(response_num_list, response)]

    for response_num_list, response in response_list:
        for response_number in response_num_list:
            logging.info("Making message {} for {} with num_list {}".format(response, response_number, response_num_list))

            '''Make message'''
            outgoing_message = Message(From=SERVER_NUMBER,
                                       To=response_number,
                                       Body=response)
            outgoing_message.put()
            logging.info(response)

            '''Send message'''
            client.messages.create(
                to=response_number,
                from_=SERVER_NUMBER,
                body=response)
            logging.info(response)

    return "Welcome to SAMSU assassins. The site is up and working.\
        Have a nice day."

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


    response_num_list = [key.id() for key in Player.query(ndb.AND(Player.state=="ALIVE",\
            Player.invul==False) ).fetch(keys_only=True)]
    response = "{} has been bombed at {}. If you were there, [REPLY {}] Y.".format(
        action.place,
        Util.utc_to_chi(action.datetime).strftime("%m-%d %I:%M%p"),
        action_key.id())

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
    req_key = request.form.get("id", "")
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
    logging.info(inv)
    target_num = inv.target
    logging.info(target_num)
    target = Player.get_by_id(target_num)
    medic = Player.get_by_id(inv.medic)
    logging.info(medic)
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
        logging.info("INVUL worker: Triggering 8 hour INVUL for target {} at {}".format(target.codename, datetime.now()))
        inv.in_effect = True
        inv_key = inv.put()
        task = taskqueue.Task(url="/invul", params={"id": inv_key.id()}, eta=inv.end_time)
        task.add(queue_name="invul")

        logging.info("Task queue okay")
        logging.info(target)
        target.invul = True
        target.put()

        logging.info("target set okay")
        logging.info(medic)
        medic.can_set_after = Util.next_day()
        medic.put()

        logging.info("medic set okay")
        response  = "You have been granted INVUL for 8 hour from {} to {}".\
                format(Util.utc_to_chi(inv.start_time).strftime("%m-%d %I:%M%p"),\
                Util.utc_to_chi(inv.end_time).strftime("%m-%d %I:%M%p"))
        msg = Message(From=SERVER_NUMBER,
                      To=inv.target,
                      Body=response)
        msg.put()
        client.messages.create(
            to=inv.target,
            from_=SERVER_NUMBER,
            body=response)
        logging.info("message set okay")
        return "INVUL Worker"
    else:
        logging.info("INVUL worker: END 8 hour INVUL for target {} at {}".format(target.codename, datetime.now()))
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
    req_key = request.form.get("id", "")
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
    disarmed_player = Player.get_by_id(disarm.victim)
    disarmed_player.disarm = False
    disarmed_player.put()

    disarm.deprecated = True
    disarm.put()

    logging.info("DISARM Worker: Turning off disarmed state for {}".format(\
            disarm.victim))

    response = "You are no longer DISARMED. Go ahead and kill people."
    msg = Message(From=SERVER_NUMBER,
                  To=disarm.victim,
                  Body=response)
    msg.put()
    client.messages.create(
        to=disarm.victim,
        from_=SERVER_NUMBER,
        body=response)
    return "DISARM WORKER"

@app.route('/spy')
def spy():
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    ''' Get all ALIVE spies '''
    alive_spies = Player.query(ndb.AND(Player.state == "ALIVE",\
            Player.role == "SPY")).fetch()

    ''' For each spy, make and send hint '''
    for spy in alive_spies:
        if spy.state == "DEAD":
            continue
        response = Player.spy_hint(spy)
        msg = Message(From=SERVER_NUMBER,
                      To=spy.key.id(),
                      Body=response)
        msg.put()
        client.messages.create(
            to=spy.key.id(),
            from_=SERVER_NUMBER,
            body=response)

    logging.info("SPY CRON: completed send to {}".format(alive_spies))
    return "Ok"

@app.route('/start')
def start():
    teams = Team.query().fetch()
    shuffle(teams)
    for j, team in enumerate(teams):
        i = j - 1
        if j == len(teams) - 1:
            k = 0
        else:
            k = j + 1

        team.to_kill = teams[k].key.id()
        team.target_of = teams[i].key.id()
        team.put()

        team_start(team, teams[k])

    output = " -> ".join([team.key.id() for team in teams])
    output += "\n\n"

    players = Player.query().fetch()
    for player in players:
        output += "{}\n".format(player)
        player.put()

    return output


def team_start(team, target_team):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    message = "Welcome to SAMSU assassins 2016. Your target is team {}:\n".\
            format(target_team.key.id())
    target_team = [target_team.sniper, target_team.medic, target_team.demo, target_team.spy]

    for target in target_team:
        if target == "":
            continue
        target_player = Player.get_by_id(target)
        message += "{} - {}".format(target_player.realname, target_player.codename)

    team_players = [team.sniper, team.medic, team.demo, team.spy]
    for p in team_players:
        if p == "":
            continue

        msg = Message(From=SERVER_NUMBER,
                      To=p,
                      Body=message)
        msg.put()
        client.messages.create(
            to=p,
            from_=SERVER_NUMBER,
            body=message)


# DEPRECATED
# @app.route("/admin/players", methods=['GET', 'POST'])
# def admin_players():
#     players = Player.query().fetch()
#     return render_template("players.html", players=players)
#     # TODO: link player objects to individual objects
#
# @app.route("/admin/teams", methods=['GET', 'POST'])
# def admin_teams():
#     teams = Team.query().fetch()
#     print teams
#     return render_template("teams.html", teams=teams)
#
# @app.route("/admin/new_player", methods=['GET', 'POST'])
# def new_player_form():
#     form = PlayerForm()
#     return render_template("player_form.html", playername="New Player", form=form)
#
# @app.route("/admin/players/<name>/edit", methods=['GET', 'POST'])
# def player_form(name):
#     player = Player.get_by_id(name)
#     form = PlayerForm(obj=player)
#     if form.validate_on_submit():
#         print form
#         return "FOO"
#     return render_template("player_form.html", playername=name, form=form)
#
# @app.route("/admin/teams/<name>/edit", methods=['GET', 'POST'])
# def team_form(name):
#     team = Team.get_by_id(name)
#     form = TeamForm(obj=team)
#     return render_template("team_form.html", teamname=name, form=form)
#
# @app.route("/admin/new_team", methods=['GET', 'POST'])
# def new_team_form(name):
#     form = TeamForm()
#     return render_template("team_form.html", teamname=name, form=form)
#
# @app.route("/admin/<item_pair>", methods=['GET', 'POST'])
# def item_form(item_pair):
#     item = item_pair[0]
#     item_type = item_pair[1]
#
#     if item == None:
#         return "Item of None Type"
#     if item_type == "INVUL":
#         if item != None:
#             form = InvulForm(obj=item)
#         else:
#             form = InvulForm()
#     elif item_type == "DISARM":
#         if item != None:
#             form = DisarmForm(obj=item)
#         else:
#             form = DisarmForm()
#     elif item_type == "BOMB":
#         if item != None:
#             form = BombForm(obj=item)
#         else:
#             form = BombForm()
#     return render_template("item_form.html", name=name, form=form)

@app.route("/test/populateDB")
def populate():
    today = Util.next_day() - timedelta(days=1)

    team1 = Team(id = "Team1", to_kill="Team2", target_of="Team3")
    p1a = Player(id="+1", realname="player1a", codename="p1a",\
       team="Team1", state="ALIVE", role="DEMO", can_set_after=today)
    team1.demo = "+1"
    p1a.put()
    p1b = Player(id="+2", realname="player1b", codename="p1b",\
       team="Team1", state="ALIVE", disarm=True, role="SNIPER",\
       can_set_after=today)
    team1.sniper="+2"
    p1b.put()
    p1c = Player(id="+3", realname="player1c", codename="p1c",\
       team="Team1", state="ALIVE", role="MEDIC", can_set_after=today)
    team1.medic="+3"
    p1c.put()
    team1.put()

    # Make Team 2 and populate with player 2a, 2b, 2c.
    # p2a is ALIVE p2b is DEAD
    # p2c is INVUL
    team2 = Team(id="Team2", to_kill="Team3", target_of="Team1")
    p2a = Player(id="+4", realname="player2a", codename="p2a",\
       team="Team2", state="ALIVE", role="DEMO", can_set_after=today)
    team2.demo = "+4"
    p2a.put()
    p2b = Player(id="+5", realname="player2b", codename="p2b",\
       team="Team2", state="ALIVE", role="SNIPER", can_set_after=today)
    team2.sniper="+5"
    p2b.put()
    p2c = Player(id="+6", realname="player2c", codename="p2c",\
       team="Team2", state="ALIVE", invul=True, role="MEDIC",\
       can_set_after=today)
    team2.medic="+6"
    p2c.put()
    team2.put()

    # Make Team 3 and populate with player 3a, 3b, 3c.
    team3 = Team(id="Team3", to_kill="Team1", target_of="Team2")
    p3a = Player(id="+7", realname="player3a", codename="p3a",\
       team="Team3", state="ALIVE", role="DEMO", can_set_after=today)
    team3.demo = "+7"
    p3a.put()
    p3b = Player(id="+8", realname="player3b", codename="p3b",\
       team="Team3", state="ALIVE", role="SPY", can_set_after=today)
    team3.sniper="+8"
    p3b.put()
    p3c = Player(id="+9", realname="player3c", codename="p3c",\
       team="Team3", state="ALIVE", role="MEDIC", can_set_after=today)
    team3.medic="+9"
    p3c.put()
    team3.put()

    wh = Player(id="+13127310539")
    wh.state = "ALIVE"
    wh.put()

    return "Players/Team put"

@app.route("/test/seed")
def seed():
    team = Team(id="SeedTeam", to_kill="SeedTeam2", target_of="SeedTeam0", sniper="P1", medic="P2", demo="P3", spy="P4" )
    team.put()
    player = Player(id="+12345678", team="SeedTeam", realname="Player1", codename="P1", state="ALIVE", role="SNIPER")
    player.put()
    return "Done"

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e),z500
