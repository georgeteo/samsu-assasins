from tests.fixture import AssassinsTestCase
from model.reply import Reply
from mock import patch
from model.actions import Action
from model.error import *
from model.player import Player
from model.disarm import Disarm
from model.kill import Kill

class TestReply(AssassinsTestCase):
    """ Test for Reply.py """
    
    @patch.object(Action, 'get_by_id')
    def test_invalid_ref_number(self, mock_action_get_by_id):
        """ Invalid ref number, cannot find action """
        mock_action_get_by_id.return_value = None
        
        with self.assertRaises(ReplyError) as e:
            Reply.handler("1", "Y", None)
        self.assertEquals("Reply ref num is invalid. Ref num: 1", e.exception.message)
        
    @patch.object(Action, 'get_by_id')
    def test_invalid_response(self, mock_action_get_by_id):
        """ Response is not Y, y, N, n """
        ref = "1"
        mock_action_get_by_id.return_value = Action()

        with self.assertRaises(ReplyError) as e:
            Reply.handler(ref, ["F"], Player())
        self.assertEquals(e.exception.message, "Reply {} is invalid. Ref num: {}".\
                format("F", ref))

    @patch.object(Disarm, 'reply_handler') 
    @patch.object(Action, 'get_by_id') 
    def test_disarm(self, mock_action_get_by_id, mock_disarm_handler):
        """ Test disarm """    
        ref = "1"
        action = Action()
        action.action = "DISARM"
        mock_action_get_by_id.return_value = action
        mock_disarm_handler.return_value = None # Don't care about response because handled by other unit tests.

        Reply.handler(ref, ["Y"], Player())
        mock_disarm_handler.assert_called_once_with(action, "Y")


    # TODO: check push
    @patch.object(Kill, 'reply_handler')
    @patch.object(Action, 'get_by_id')
    def test_valid_kill_no_team_push(selfi, mock_action_get_by_id, mock_kill_handler):
        """ Valid kill, but team not killed """
        ref = "1"
        action = Action()
        action.action = "KILL"
        mock_action_get_by_id.return_value = action
        mock_kill_handler.return_value = None

        Reply.handler(ref, ["Y"], Player())
        mock_kill_handler.assert_called_once_with(action, "Y")
        
    def test_valid_kill_with_team_push(self):
        """ Valid kill and team is dead. Need to push """
        pass

    def test_valid_bomb_no_team_push(self):
        """ Valid bomb, but team not killed """
        pass

    def test_valid_bomb_with_team_push(self):
        """ Valid kill and team is dead. Need to push """
        pass
    

    
