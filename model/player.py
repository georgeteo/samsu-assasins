from google.appengine.ext import ndb


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
    role = ndb.StringProperty()
    killed = ndb.JsonProperty(default=[])


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
