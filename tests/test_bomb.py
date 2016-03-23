from tests.fixture import AssassinsTestCase
from model.bomb import Bomb
from model.error import ActionError
import re
from model.util import Util

import logging

class TestBomb(AssassinsTestCase):
    """ Test Bomb functionality.
        TODO: how to check state is correctly not changed? """
    
    def test_error_role_is_not_demo(self):
        """ Attacker is not role DEMO, Error."""
        attacker = self.p1b
        params = ["Here", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are not the DEMO")
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_attacker_is_dead(self):
        """ Attacker is DEAD, Error. """
        attacker = self.p1a
        attacker.state = "DEAD"
        attacker.put()
        params = ["Here", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DEAD")
        self.assertEqual(len(self.bomb_queue), 0)
            
    def test_error_attacker_bomb_time_invalid(self):
        """ Attacker wants to set a bomb but his bomb quota for today is expired"""
        attacker = self.p1a
        attacker.can_set_after = Util.next_day()
        params = ["Here", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You cannot set the bomb at this time. Please wait until midnight.")
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_time_is_before_now(self):
        """ Attacker wants to set a bomb back in time """
        attacker = self.p1a
        tomorrow = Util.next_day()
        params = ["Here", str(tomorrow.month), str(tomorrow.day),\
                str(tomorrow.hour), str(tomorrow.minute)]
        with self.assertRaises(ActionError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You cannot set a time {} before current time {}".format(tomorrow, Util.utc_to_chi(datetime.now())))
        self.assertEqual(len(self.bomb_queue), 0)

    def test_error_attacker_is_disarm(self):
        """ Attacker is diarmed trying to set a bomb: use p2a as attacker """
        attacker = self.p2a
        params = ["Here", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Bomb.handler(attacker, params)
        self.assertEqual(e.exception.message, "You are DISARM")
        self.assertEqual(len(self.bomb_queue), 0)

    def good_bomb(self):
        """ Good attacker set good bomb. """
        attacker = self.p1a
        later = Util.utc_to_chi(datetime.now())
        params = ["Here", str(later.month), str(later.day), \
                str(later.hour + 1), str(later.minute)]
        Bomb.handler(attacker, params)
        self.assertEqual(len(self.bomb_queue), 1)


        
        


