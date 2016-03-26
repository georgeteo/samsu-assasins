import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

from model.player import Player, Team
from datetime import timedelta
from model.util import Util


class AssassinsTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        ndb.get_context().clear_cache()
        self.testbed.init_taskqueue_stub(root_path=".")
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        # Setup fixture
        today = Util.next_day() - timedelta(days=1)

        # Make Team 1 and populate with player 1a, 1b, 1c. 
        # p1a is ALIVE and DEMO
        # p1b is ALIVE, DISARM, and SNIPER
        # p1c is ALIVE, MEDIC
        self.team1 = Team(id = "Team1", to_kill="Team2", target_of="Team3")
        self.p1a = Player(id="+1", realname="player1a", codename="p1a",\
                team="Team1", state="ALIVE", role="DEMO", can_set_after=today)
        self.team1.demo = "+1"
        self.p1a.put()
        self.p1b = Player(id="+2", realname="player1b", codename="p1b",\
                team="Team1", state="ALIVE", disarm=True, role="SNIPER",\
                can_set_after=today)
        self.team1.sniper="+2"
        self.p1b.put()
        self.p1c = Player(id="+3", realname="player1c", codename="p1c",\
                team="Team1", state="ALIVE", role="MEDIC", can_set_after=today)
        self.team1.medic="+3"
        self.p1c.put()
        self.team1.put()

        # Make Team 2 and populate with player 2a, 2b, 2c.
        # p2a is ALIVE
        # p2b is DEAD
        # p2c is INVUL
        self.team2 = Team(id="Team2", to_kill="Team3", target_of="Team1")
        self.p2a = Player(id="+4", realname="player2a", codename="p2a",\
                team="Team2", state="ALIVE", role="DEMO", can_set_after=today)
        self.team2.demo = "+4"
        self.p2a.put()
        self.p2b = Player(id="+5", realname="player2b", codename="p2b",\
                team="Team2", state="DEAD", role="SNIPER", can_set_after=today)
        self.team2.sniper="+5"
        self.p2b.put()
        self.p2c = Player(id="+6", realname="player2c", codename="p2c",\
                team="Team2", state="ALIVE", invul=True, role="MEDIC",\
                can_set_after=today)
        self.team2.medic="+6"
        self.p2c.put()
        self.team2.put()
        
        # Make Team 3 and populate with player 3a, 3b, 3c.
        self.team3 = Team(id="Team3", to_kill="Team1", target_of="Team2")
        self.p3a = Player(id="+7", realname="player3a", codename="p3a",\
                team="Team3", state="ALIVE", role="DEMO", can_set_after=today)
        self.team3.demo = "+7"
        self.p3a.put()
        self.p3b = Player(id="+8", realname="player3b", codename="p3b",\
                team="Team3", state="ALIVE", role="SPY", can_set_after=today)
        self.team3.sniper="+8"
        self.p3b.put()
        self.p3c = Player(id="+9", realname="player3c", codename="p3c",\
                team="Team3", state="ALIVE", role="MEDIC", can_set_after=today)
        self.team3.medic="+9"
        self.p3c.put()
        self.team3.put()

    def tearDown(self):
        self.testbed.deactivate()
        
