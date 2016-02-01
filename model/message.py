from google.appengine.ext import ndb
from model.player import Player
import logging


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
    Picture = ndb.StringProperty(default="")
