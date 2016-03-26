from tests.fixture import AssassinsTestCase
from model.Reply import Reply
from mock import Mock

class TestReply(AssassinsTestCase):
    """ Test for Reply.py """
    def setUp(self):
        super(TestReply, self).setUp()

        action = Action()
        self.ref = action.put()
        self.action = action

    def test_invalid_ref_number(self):
        """ Invalid ref number, cannot find action """

        pass

    def test_invalid_response(self):
        """ Response is not Y, y, N, n """
        pass

    def test_valid_kill_no_team_push(self):
        """ Valid kill, but team not killed """
        pass

    def test_valid_kill_with_team_push(self):
        """ Valid kill and team is dead. Need to push """
        pass

    def test_valid_bomb_no_team_push(self):
        """ Valid bomb, but team not killed """
        pass

    def test_valid_bomb_with_team_push(self):
        """ Valid kill and team is dead. Need to push """
        pass
    

    
