from tests.fixture import AssassinsTestCase
from model.disarm import Disarm
from model.player import Player
from model.error import *
import re
from model.util import Util
from model.actions import Action
from datetime import datetime, timedelta

import logging

class TestDisarm(AssassinsTestCase):
    """ Test Disarm Functionality """

    def setUp(self):
        super(TestDisarm, self).setUp()
        action = Action()
        action.attacker = "+4"
        action.action = "DISARM"
        action.victim = "+1"
        action.datetime = datetime.now()
        action.put()
        self.action = action

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
                r"\[REPLY \d*\] player2a claimed to have disarm you. Reply Y\/N.")

    def test_reply_disarm_Y(self):
        """ Test disarm reply Y """
        later = Util.utc_to_chi(self.action.datetime + timedelta(hours=1))

        ret = Disarm.reply_handler(self.action, "Y")
        self.assertEqual(1, len(ret))
        self.assertEqual(ret[0][0], "+1")
        self.assertEqual(ret[0][1], "You have been DISARM until {}".format(\
                later.strftime("%m-%d %I:%M%p")))
        self.assertEqual(len(self.taskqueue_stub.get_filtered_tasks(\
                queue_names='disarm')), 1)
        self.assertEqual(self.p1a.disarm, True)

    def test_reply_disarm_y(self):
        """ Test disarm reply y """
        later = Util.utc_to_chi(self.action.datetime + timedelta(hours=1))

        ret = Disarm.reply_handler(self.action, "y")
        self.assertEqual(1, len(ret))
        self.assertEqual(ret[0][0], "+1")
        self.assertEqual(ret[0][1], "You have been DISARM until {}".format(\
                later.strftime("%m-%d %I:%M%p")))
        self.assertEqual(self.p1a.disarm, True)
        self.assertEqual(len(self.taskqueue_stub.get_filtered_tasks(\
                queue_names='disarm')), 1)
        
    def test_reply_disarm_N(self):
        """ Test disarm reply N """
        ret = Disarm.reply_handler(self.action, "N")
        self.assertEqual(1, len(ret))
        self.assertEqual(ret[0][0], self.action.attacker)
        self.assertEqual(ret[0][1], "Your DISARM target claims he was not "
                "disarmed by you.")
        self.assertEqual(self.p1a.disarm, False)
        self.assertEqual(len(self.taskqueue_stub.get_filtered_tasks(\
                queue_names='disarm')), 0)
    
    def test_reply_disarm_n(self):
        """ Test disarm reply n """
        ret = Disarm.reply_handler(self.action, "n")
        self.assertEqual(1, len(ret))
        self.assertEqual(ret[0][0], self.action.attacker)
        self.assertEqual(ret[0][1], "Your DISARM target claims he was not "
                "disarmed by you.")
        self.assertEqual(self.p1a.disarm, False)
        self.assertEqual(len(self.taskqueue_stub.get_filtered_tasks(\
                queue_names='disarm')), 0)

