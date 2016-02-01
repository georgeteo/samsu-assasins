from google.appengine.ext import ndb
from model.error import ActionError
from google.appengine.ext import ndb
from google.appengine.api import Task
from datetime import datetime

class Bomb(ndb.Model):
    attacker = ndb.StringProperty()
    place = ndb.StringProperty()
    time = ndb.DateTimeProperty()
    trigger = ndb.BooleanProperty(default=False)

    @staticmethod
    def handler(attacker, params):
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

        task = Task(url="/bomb", params={"id": bomb_key}, eta=time)
        task.add(queue_name="bomb")

        return bomb.attacker, "Your bomb in {} will explode at {}-{} {}:{}".format(
            bomb.place, time.month, time.day, time.hour, time.minute)



