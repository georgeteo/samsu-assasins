import logging
from model.util import Util
from model.player import Team, Player
from model.error import *
from model.actions import Action
from datetime import datetime

WEI_HAN = "+13127310539"

class Snipe(object):
    """
    SNIPE <attacker codename> <victim codename>
    """

    @classmethod
    def handler(cls, attacker, victim_codename):
        logging.info("SNIPE start.")
        
        victim = Util.get_victim(victim_codename)

        """ validation """ 
        outgoing = []
        try:
            Kill.validate_kill(attacker, victim)
            if attacker.role != "SNIPER":
                raise MeError("not SNIPER")
        except (TeamError, MeError, TargetError) as message:
            outgoing.append(([WEI_HAN], message))
            outgoing.append(([attacker.key.id()], message))
            return outgoing
        except:
            message = "[ERR] Unknown Error in SNIPE"
            outgoing.append(([WEI_HAN], message))
            outgoing.append(([attacker.key.id()], message))
            return outgoing

        action = Action()
        action.attacker = attacker.key.id()
        action.action = "SNIPE"
        action.victim = victim.key.id()
        action.datetime = datetime.now()
        action_key = action.put()

        message = "{} has been SNIPED.".format(victim_codename))
        outgoing.append([victim.key.id()], "You have been SNIPED. (Ref {}).".\
                format(action_key))
        outgoing.append("*", message)
        return outgoing
