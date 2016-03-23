from tests.fixture import AssassinsTestCase
from model.bomb import Bomb
from model.error import *
import re
from model.util import Util

import logging

class TestDisarm(AssassinsTestCase):
    """ Test Disarm Functionality """

    def test_error_target_wrong_team(self):
        """ Target on the wrong team """ 
        attacker = self.p2a
        params = ["p3a"]
        with self.assertRaises(TeamError) as e:
            Disarm.handler(attacker, params)
        self.assertEqual(e.exception.message, "Invalid Team. You cannot do that action to someone on that team.")
        

    def test_error_target_is_dead(self):
        """ Target is already dead """
        attacker = self.p2a
        params = ["p1a"]
        target = self.p1a
        target.state = "DEAD"
        target.put()
        with self.assertRaises(TargetError) as e:
            Disarm.handler(attacker, params)
        self.assertEqual(e.exception.message, "Your target is DEAD")
    
    def test_error_dismarer_is_dead(self):
        """ Attacker is a dead """
        attacker = self.p2b
        params = ["p1a"]
        with self.assertRaises(MeError) as e:
            Disarm.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")

    def test_good_disarm(self):
        """ Good disarmer with good target """
        attacker = self.p2a
        params = ["p1a"]
        ret = Disarm.handler(attacker, params)
        self.assertEqual(1, len(ret))
        self.assertEqual("+1", ret[0][0])
        self.assertRegexpMatches(ret[0][1], \
                r"\[REPLY \d*\] player2a claimed to have disarmed you. Reply Y\/N.",\
                "Msg was: {}".format(ret[0][1]))
        
        
    
