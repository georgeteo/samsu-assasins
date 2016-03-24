from tests.fixture import AssassinsTestCase
from model.Reply import Reply

class TestReply(AssassinsTestCase):
    """ Test for Reply.py """
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
    

    
