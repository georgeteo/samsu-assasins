from google.appengine.ext import ndb
from model.player import Player
import logging
from datetime import datetime


class Message(ndb.Model):
    '''
    Message object.
    Key: TwilMessageid
    Fields:
        From phone number
        To Phone number
        Body raw message body
        Picture image string
    '''
    From = ndb.StringProperty()
    To = ndb.StringProperty()
    Body = ndb.StringProperty()
    datetime = ndb.DateTimeProperty(default=datetime.now())
