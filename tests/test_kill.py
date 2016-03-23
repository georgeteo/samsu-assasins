from tests.fixture import AssassinsTestCase
from model.kill import Kill
from model.error import *
import re
from model.actions import Action

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
        with self.assertRaises(TargetError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Your target is DEAD")
    
    def test_good_attacker_invul_target(self):
        """ Good attacker invul target: p1a attacks p2c """
        attacker = self.p1a
        params = ["p2c"]
        with self.assertRaises(TargetError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Your target is INVUL")
    
    def test_disarm_attacker_good_target(self):
        """ Disarm attacker good target: p1b attacks p2a """
        attacker = self.p1b
        params = ["p2a"]
        with self.assertRaises(MeError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DISARM")
    
    def test_dead_attacker_good_target(self):
        """ Dead attacker good target: p1a attack p2a """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = ["p2a"]
        with self.assertRaises(MeError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")

    def test_dead_attacker_bad_target(self):
        """ Dead attacker dead target: p1a attack p2b """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = ["p2b"]
        with self.assertRaises(MeError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")

    def test_good_attacker_target_wrong_team(self):
        """ Target is on the wrong team """
        attacker = self.p1a
        params = ["p3b"]
        with self.assertRaises(TeamError) as e:
            Kill.handler(attacker, params)
        self.assertEqual(e.exception.message, "Invalid Team. You cannot do that action to someone on that team.")

    """ Test Kill reply """
    def test_kill_reply_Y(self):
        """ Kill reply Y response """
        action = Action()
        action.victim = "+1"
        action.put()

        ret = Kill.reply_handler(action, "Y")
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "*")
        self.assertEqual(ret[0][1], "p1a has been killed")
        self.assertEqual(self.p1a.state, "DEAD")
        
    def test_kill_reply_y(self):
        """ Kill reply y response """
        action = Action()
        action.victim = "+1"
        action.put()

        ret = Kill.reply_handler(action, "y")
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "*")
        self.assertEqual(ret[0][1], "p1a has been killed")
        self.assertEqual(self.p1a.state, "DEAD")
        
    def test_kill_reply_N(self):
        """ Kill reply N response """
        action = Action()
        action.attacker = "+1"
        action.victim = "+4"
        action.put()

        ret = Kill.reply_handler(action, "N")
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "+1")
        self.assertEqual(ret[0][1], "Your victim claims that he/she was not "
            "killed. Please check that you have the correct codename")
        self.assertEqual(self.p2a.state, "ALIVE")
    
    def test_kill_reply_n(self):
        """ Kill reply n response """
        action = Action()
        action.attacker = "+1"
        action.victim = "+4"
        action.put()

        ret = Kill.reply_handler(action, "n")
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "+1")
        self.assertEqual(ret[0][1], "Your victim claims that he/she was not "
            "killed. Please check that you have the correct codename")
        self.assertEqual(self.p2a.state, "ALIVE")
