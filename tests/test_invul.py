from tests.fixture import AssassinsTestCase
from model.invul import Invul
from model.error import ActionError
import re

import logging

class TestInvul(AssassinsTestCase):
    """ Test Invul functionality """

    def test_invul_not_medic(self):
        """ INVUL command must come from medic """
        medic = self.p1a
        params = ["p1c", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You are not the MEDIC")
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_medic_not_alive(self):
        """ MEDIC must be arrive when invoking command """
        medic = self.p1c
        medic.state = "DEAD"
        medic.put()
        params = ["p1a", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You are DEAD")
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_target_not_alive(self):
        """ Target must be alive """
        medic = self.p1c
        target = self.p1a
        target.state = "DEAD"
        target.put()
        params = ["p1a", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "Your target is DEAD")
        self.assertEqual(len(self.invul_queue), 0)
        
    def test_invul_error_time_before_valid_time(self):
        """ MEDIC can only INVUL one person per 24 hour period """
        medic = self.p1c
        medic.can_set_after = Util.next_day()
        medic.put()
        params = ["p1a", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You cannot set invul at this time. Please wait until midnight.")
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_error_time_before_now(self):
        """ MEDIC can only INVUL a time in the future """
        medic = self.p1c
        tomorrow = Util.next_day()
        params = ["p1a", str(tomorrow.month), str(tomorrow.day),\
                str(tomorrow.hour), str(tomorrow.minute)]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You cannot set a time {} before current time {}".format(tomorrow, Util.utc_to_chi(datetime.now())))
        self.assertEqual(len(self.invul_queue), 0)


    def test_not_same_team(self):
        """ MEDIC can only INVUL same team """
        medic = self.p1c
        params = ["p2a", "1", "1", "1", "1"]
        with self.assertRaises(ActionError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "Invalid Team. Can only do that to someone on the same team.") 
        self.assertEqual(len(self.invul_queue), 0)

    def test_good_invul(self):
        """ GOOD test """
        medic = self.p1c
        now = Util.utc_to_chi(datetime.now())
        params = ["p1a", str(now.month), str(now.day), \
                str(now.hour + 1), str(now.minute)]
        Invul.handler(medic, params)
        self.assertEqual(len(self.invul_queue),1)
