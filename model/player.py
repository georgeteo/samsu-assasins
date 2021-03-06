from google.appengine.ext import ndb
from datetime import datetime
import random
import logging

WEI_HAN = "+13127310539"

class Player(ndb.Model):
    '''Pllayer object is child of a Team object.
    Key: phone number
    Has:
        team
        state - ALIVE, DEAD, INVUL, DISARM
        role - DEMO, SNIPER, MEDIC
        realname
        codename
        killed - list of people killed []
    Parent: team'''
    team = ndb.StringProperty()
    realname = ndb.StringProperty()
    codename = ndb.StringProperty()
    state = ndb.StringProperty()
    invul = ndb.BooleanProperty(default=False)
    disarm = ndb.BooleanProperty(default=False)
    role = ndb.StringProperty()
    can_set_after = ndb.DateTimeProperty(default=datetime.min)
    item = ndb.IntegerProperty(default=0)
    killed_by = ndb.StringProperty(default="")
    killed = ndb.StringProperty(repeated=True)

    @classmethod
    def spy_hint(cls, spy):
        ''' Make spy hint '''
        if random.randint(0,1) == 1:
            logging.info("Spy hint: attacker-target hint.")
            return Player.spy_hint_attacker_target(spy)
        else:
            logging.info("Spy hint: realname-codename hint.")
            return Player.spy_hint_names(spy)

    @classmethod
    def spy_hint_attacker_target(cls, spy):
        ''' Spy hint a attacking b '''
        random_attackers = Player.query(Player.team != spy.team).fetch()
        if len(random_attackers) == 0:
            return "SPY: No more new attacker-target hints."
        one_attacker = random.choice(random_attackers)
        attacker_team = Team.get_by_id(one_attacker.team)
        alive_targets = Player.query(ndb.AND(Player.team == attacker_team.to_kill,\
                Player.state == "ALIVE")).fetch()
        if len(alive_targets) == 0:
            return "SPY: No one is left alive on any other team."
        one_target = random.choice(alive_targets)
        msg = "SPY: {} wants to kill {}.".format(one_attacker.realname,\
                one_target.realname)
        return msg

    @classmethod
    def spy_hint_names(cls, spy):
        ''' Spy hint realname - codename '''
        spy_team = Team.get_by_id(spy.team)
        random_people = Player.query(ndb.AND(Player.team != spy.team,\
                Player.team != spy_team.to_kill)).fetch()
        if len(random_people) == 0:
            return "SPY: No more new realname-codename hints."
        random_person = random.choice(random_people)
        logging.info("Random person: {}".format(random_person))
        msg = "SPY: {}'s codename is {}.".format(random_person.realname,\
                random_person.codename)
        return msg

class Team(ndb.Model):
    '''Team objectx
    Key: team_name
    Has:
        to_kill
        target_of
        sniper
        medic
        demo
    Child: Player'''
    to_kill = ndb.StringProperty(default="")
    target_of = ndb.StringProperty(default="")
    sniper = ndb.StringProperty(default="")
    medic = ndb.StringProperty(default="")
    demo = ndb.StringProperty(default="")
    spy = ndb.StringProperty(default="")

    @classmethod
    def push(cls, team):
        """ Returns push kill message or [] """
        logging.info("Push start")
        logging.info("Pushed called for team: {}".format(team))

        count_my_team = 0
        for player_id in Team.get_players(team):
            player = Player.get_by_id(player_id)
            logging.info("Push: looking at player {}".format(player_id))
            if player.state == "ALIVE": # if player is alive, no push
                logging.info("He is alive.")
                count_my_team += 1

        if count_my_team == 1:
            logging.info("Team key id: {} - to kill: {}".format(team.key.id(), team.to_kill))
            if team.key.id() == team.to_kill:
                logging.info("Push winner 1")
                winner = Player.query(Player.state == "ALIVE").get()
                msg = "Congratulations. You are the winner."
                return [(winner.key.id(), msg), (WEI_HAN, "Game is over. Please check that winner got the message.")]
        if count_my_team > 0:
            return []

        # Else, all players on this team DEAD, push
        aggressor_team = Team.get_by_id(team.target_of)
        target_team = Team.get_by_id(team.to_kill)

        logging.info("Before team update:")
        logging.info("Aggressor: {}".format(aggressor_team))
        logging.info("This team: {}".format(team))
        logging.info("Target team: {}".format(target_team))

        aggressor_team.to_kill = target_team.key.id()
        aggressor_team.put()

        target_team.target_of = aggressor_team.key.id()
        target_team.put()

        team.to_kill = ""
        team.target_of = ""
        team.put()

        logging.info("Before team update:")
        logging.info("Aggressor: {}".format(aggressor_team))
        logging.info("This team: {}".format(team))
        logging.info("Target team: {}".format(target_team))

        logging.info("Making message")
        message = "Congratulations. Your next target is team {}:\n".format(\
                target_team.key.id())
        count = 0
        for target_id in Team.get_players(target_team):
            target_player = Player.get_by_id(target_id)
            logging.info("Looking at target player: {}".format(target_player.realname))
            if target_player.state == "ALIVE":
                logging.info("He is {}.".format(target_player.state))
                count += 1
                message += "{} - {}\n".format(target_player.realname,\
                        target_player.codename)
            logging.info("He is {}.".format(target_player.state))
        logging.info("End message make. Message is: {}".format(message))

        push_messages = []
        if count == 1 and aggressor_team.to_kill == aggressor_team.key.id():
            logging.info("Push winner 2")
            message = "Congratulations. You are the winner."
            push_messages.append((WEI_HAN, "Game is over. Please check that winner got the message."))

        logging.info("Making push messages to send.")
        for aggressor_id in Team.get_players(aggressor_team):
            logging.info("Looking at {}".format(aggressor_id))
            if Player.get_by_id(aggressor_id).state == "ALIVE":
                logging.info("He is alive. Append: {}".format((aggressor_id, message)))
                push_messages.append((aggressor_id, message))
            logging.info("He is dead.")

        logging.info("Push complete: {}".format(push_messages))

        return push_messages


    @classmethod
    def get_players(cls, team):
        output = [team.sniper, team.medic, team.demo, team.spy]
        return [o for o in output if o != ""]
