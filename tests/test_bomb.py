from tests.fixture import AssassinsTestCase
from model.bomb import Bomb
from model.error import *
import re
from model.util import Util
from datetime import datetime, timedelta

import logging

class TestBomb(AssassinsTestCase):
    """ Test Bomb functionality.
        TODO: how to check state is correctly not changed? """

    def setUp(self):
        super(TestBomb, self).setUp()
        test_dt = Util.utc_to_chi(datetime.now()) + timedelta(minutes=1)
        self.default_params = ["Here", str(test_dt.month), str(test_dt.day),\
                str(test_dt.hour), str(test_dt.minute)]
        
        action = Action()
        action.attacker = "+1"
        action.action = "BOMB"
        action.victim = "*"
        action.datetime = datetime.now()
        action.place = "Place"
        action.put()
        self.action = action
    
    def test_error_role_is_not_demo(self):
        """ Attacker is not role DEMO, Error."""
        attacker = self.p1b
        params = self.default_params
        with self.assertRaises(MeError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are not DEMO")
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_attacker_is_dead(self):
        """ Attacker is DEAD, Error. """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = self.default_params
        with self.assertRaises(MeError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")
        self.assertEqual(len(self.bomb_queue), 0)
            
    def test_error_attacker_bomb_time_invalid(self):
        """ Attacker wants to set a bomb but his bomb quota for today is expired"""
        attacker = self.p1a
        attacker.can_set_after = Util.next_day()
        params = self.default_params
        with self.assertRaises(TimeError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You cannot set bomb before time {}.".\
                format(Util.utc_to_chi(attacker.can_set_after).strftime(\
                "%m-%d %I:%M%p")))
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_time_is_before_now(self):
        """ Attacker wants to set a bomb back in time """
        attacker = self.p1a
        now = Util.utc_to_chi(datetime.now()) - timedelta(hours=1)
        params = ["Here", str(now.month), str(now.day),\
                str(now.hour), str(now.minute)]
        with self.assertRaises(TimeError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You cannot set {} before time {}."\
                .format(now.strftime("%m-%d %I:%M%p"),\
                Util.utc_to_chi(datetime.now()).strftime("%m-%d %I:%M%p")))
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_attacker_is_disarm(self):
        """ Attacker is diarmed trying to set a bomb: use p2a as attacker """
        attacker = self.p1a
        attacker.disarm = True
        attacker.put()
        params = self.default_params
        with self.assertRaises(MeError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DISARM")
        self.assertEqual(len(self.bomb_queue), 0)

    def good_bomb(self):
        """ Good attacker set good bomb. """
        attacker = self.p1a
        later = Util.utc_to_chi(datetime.now())
        params = self.default_params
        Bomb.handler(attacker, params)
        self.assertEqual(len(self.bomb_queue), 1)

    """ Test Bomb reply """
    def test_bomb_reply_Y(self):
        """ Bomb reply Y response """
        ret = Bomb.reply_handler(self.action, "Y", self.p2a)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "*")
        self.assertEqual(ret[0][1], "p2a has been killed")
        self.assertEqual(self.p2a.state, "DEAD")
        
    def test_bomb_reply_y(self):
        """ Bomb reply y response """
        ret = Bomb.reply_handler(self.action, "y", self.p2a)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0][0], "*")
        self.assertEqual(ret[0][1], "p2a has been killed")
        self.assertEqual(self.p2a.state, "DEAD")
        
    def test_bomb_reply_N(self):
        """ Bomb reply N response """
        ret = Bomb.reply_handler(self.action, "N", self.p2a)
        self.assertEqual(len(ret), 0)
        self.assertEqual(self.p2a.state, "ALIVE")
    
    def test_bomb_reply_n(self):
        """ Bomb reply n response """
        ret = Bomb.reply_handler(self.action, "n", self.p2a)
        self.assertEqual(len(ret), 0)
        self.assertEqual(self.p2a.state, "ALIVE")
        
        


