from tests.fixture import AssassinsTestCase
from model.invul import Invul
from model.error import ActionError
import re
from model.util import Util

import logging

class TestInvul(AssassinsTestCase):
    """ Test Invul functionality """

    def setUp(self):
        super(TestInvul, self).setUp()
        test_dt = Util.utc_to_chi(datetime.now()) + timedelta(minutes=1)
        self.default_params = ["p1a", str(test_dt.month), str(test_dt.day),\
                str(test_dt.hour), str(test_dt.minute)]

    def test_invul_not_medic(self):
        """ INVUL command must come from medic """
        medic = self.p1a
        params = self.default_params 
        params[0] = "p1c"
        with self.assertRaises(MeError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You are not MEDIC")
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_medic_not_alive(self):
        """ MEDIC must be arrive when invoking command """
        medic = self.p1c
        medic.state = "DEAD"
        medic.put()
        params = self.default_params
        with self.assertRaises(MeError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You are DEAD")
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_target_not_alive(self):
        """ Target must be alive """
        medic = self.p1c
        target = self.p1a
        target.state = "DEAD"
        target.put()
        params = self.default_params
        with self.assertRaises(TargetError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "Your target is DEAD")
        self.assertEqual(len(self.invul_queue), 0)
        
    def test_invul_error_time_before_valid_time(self):
        """ MEDIC can only INVUL one person per 24 hour period """
        medic = self.p1c
        medic.can_set_after = Util.next_day()
        medic.put()
        params = self.default_params
        with self.assertRaises(TimeError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You cannot set invul before time {}."\
                .format(Util.utc_to_chi(medic.can_set_after).strftime("%m-%d %I:%M%p")))
        self.assertEqual(len(self.invul_queue), 0)

    def test_invul_error_time_before_now(self):
        """ MEDIC can only INVUL a time in the future """
        medic = self.p1c
        now = Util.utc_to_chi(datetime.now()) - timedelta(hours=1)
        params = ["p1a", str(now.month), str(now.day),\
                str(now.hour), str(now.minute)]
        with self.assertRaises(TimeError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, "You cannot set {} before time {}."\
                .format(now.strftime("%m-%d %I:%M%p"),\
                Util.utc_to_chi(datetime.now()).strftime("%m-%d %I:%M%p")))
        self.assertEqual(len(self.invul_queue), 0)

    def test_not_same_team(self):
        """ MEDIC can only INVUL same team """
        medic = self.p1c
        params = self.default_params
        with self.assertRaises(TeamError) as e:
            Invul.handler(medic, params)
        self.assertEqual(e.exception.message, \
                "Invalid Team. You cannot do that action to someone on that team.")
        self.assertEqual(len(self.invul_queue), 0)

    def test_good_invul(self):
        """ GOOD test """
        medic = self.p1c
        now = Util.utc_to_chi(datetime.now())
        params = self.default_params
        Invul.handler(medic, params)
        self.assertEqual(len(self.invul_queue),1)
        # TODO: test reply string
