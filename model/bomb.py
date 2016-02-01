from google.appengine.ext import ndb
from model.error import ActionError
from google.appengine.api import taskqueue
from datetime import datetime
import logging

class Bomb(ndb.Model):
    attacker = ndb.StringProperty()
    place = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    trigger = ndb.BooleanProperty(default=False)

    @staticmethod
    def handler(attacker, params):
        if attacker.role != "DEMO":
            raise ActionError("ROLE", "DEMO")

        place = params.pop(0)
        if not place:
            raise ActionError("LOCATION", "")
        time = datetime(2016,
                        int(params[0]),
                        int(params[1]),
                        int(params[2]),
                        int(params[3]))

        bomb = Bomb()
        bomb.attacker = attacker.key.id()
        bomb.place = place
        bomb.time = time
        bomb.trigger = False

        bomb_key = bomb.put()

        task = taskqueue.Task(url="/bomb", params={"id": bomb_key}, eta=time)
        task.add(queue_name="bomb")

        logging.info("BOMB: set for {} at {}".format(time, place))

        return bomb.attacker, "Your bomb in {} will explode at {}-{} {}:{}".format(
            bomb.place, time.month, time.day, time.hour, time.minute)
