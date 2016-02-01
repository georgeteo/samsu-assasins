from google.appengine.ext import ndb
from player import Player, Team
from datetime import datetime
from error import ActionError
import logging


class Action(ndb.Model):
    '''
    Action object
    Key: default assigned by NDB
    Fields:
        attacker - phone number
        action - string
        victim - phone number
        datetime
        place
        validation
    '''
    attacker = ndb.StringProperty(required=True)
    action = ndb.StringProperty(required=True,
                                choices=set(["KILL",
                                             "DISARM",
                                             "INVUL",
                                             "SNIPE",
                                             "BOMB"]))
    victim = ndb.StringProperty(default="")
    datetime = ndb.DateTimeProperty(required=True)
    place = ndb.StringProperty(default="")
    need_validation = ndb.BooleanProperty(default=True)
    incorrect_kill = ndb.BooleanProperty(default=False)

