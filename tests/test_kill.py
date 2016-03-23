from tests.fixture import AssassinsTestCase
from model.kill import Kill
from model.error import ActionError
import re

import logging

class TestKill(AssassinsTestCase):
    """ Test Kill functionality.
        TODO: how to check state is correctly not changed? """

    def test_good_attacker_good_target(self):
        """ Good attacker good target: p1a attacks p2a """
        attacker = self.p1a
        params = ["p2a"]
        ret = Kill.handler(attacker, params)
        self.assertEqual(1, len(ret))
        self.assertEqual("+4", ret[0][0])
        self.assertRegexpMatches(ret[0][1], \
                r"\[REPLY \d*\] player1a claimed to have killed you. Reply Y\/N.",\
                "Msg was: {}".format(ret[0][1]))
    
    def test_good_attacker_dead_target(self):
        """ Good attacker dead target: p1a attacks p2b """
        attacker = self.p1a
        params = ["p2b"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Your target is DEAD")
    
    def test_good_attacker_invul_target(self):
        """ Good attacker invul target: p1a attacks p2c """
        attacker = self.p1a
        params = ["p2c"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Your target is INVUL")
    
    def test_disarm_attacker_good_target(self):
        """ Disarm attacker good target: p1b attacks p2a """
        attacker = self.p1b
        params = ["p2a"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DISARM")
    
    def test_disarm_attacker_bad_target(self):
        """ Disarm attacker bad target: p1b attacks p2b """
        attacker = self.p1b
        params = ["p2b"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DISARM")

    def test_dead_attacker_good_target(self):
        """ Dead attacker good target: p1a attack p2a """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = ["p2a"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")

    def test_dead_attacker_bad_target(self):
        """ Dead attacker dead target: p1a attack p2b """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = ["p2b"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")

    def test_good_attacker_target_wrong_team(self):
        """ Target is on the wrong team """
        attacker = self.p1a
        params = ["p3b"]
        with self.assertRaises(ActionError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Invalid Team. You cannot do that action to someone on that team.")
