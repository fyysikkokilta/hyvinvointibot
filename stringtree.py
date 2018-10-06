"""
This module contains all string and some helper functions related to messaging.
"""
import types
from collections import OrderedDict
import scoring
from scoring import GOOD_KEY, BAD_KEY, ScoreObject

RETURN_BUTTON_ID = "return_choice"

#####################
# MESSAGE CONSTANTS #
#####################

BUTTONS_ERROR_MSG = "Valitse yksi annetuista vaihtoehdoista."

RETURN_BUTTON_MESSAGE = "« Alkuun"
RETURN_MESSAGE = "alkuun"
GROUP_REPLY_MESSAGE = "Lähetä komentoja yksityisviestillä."
DID_NOT_UNDERSTAND_MESSAGE = "En ymmärrä. Käytä jotakin annetuista komennoista tai kokeile /help."
UNKNOWN_COMMAND_MESSAGE = "En ymmärrä komentoa. Käytä jotakin annetuista komennoista tai kokeile /help."
HELP_MESSAGE = "help-komento on vielä toteuttamatta lörs" #TODO
START_ADD_EVENT_MESSAGE = "Mitä olet tehnyt tänään?"

"""
The STRING_TREE object contains all possible chains of discussion. It is a dict
containing dicts. Each sub-dictionary corresponds to a message. Each dict
should have the following key-value pairs:
    msg - the message the bot sends when at this point in the conversation
        (the root node doesn't have this)
    errorMessage - a message that the bot should send when the reply wasn't
        sensible

Furthermore, each non-leaf node should have the attributes
    children - multiple choices, which the user can select from using buttons
    OR
    child AND validation_func - in this case, the user is expected to input
        free-form data, such as a number. this data should be validated using
        the function validation_func, which should return either the validated
        value (such as a number extracted from a string) or None.

If a node has neither of the above, it is assumed to be a leaf node, and the
conversation is terminated after it. A leaf node may have a key-value pair
score_func, which evaluates the score of a given conversation chain.
"""

STRING_TREE = {
    #### root has no 'msg' (good idea?)
    "msg": START_ADD_EVENT_MESSAGE,
    "errorMessage" : BUTTONS_ERROR_MSG,
    "children" : {
        #TODO: change to OrderedDict?
        "liikunta" : {
            "msg" : "Asteikolla 0-5, kuinka intensiivistä se oli?",
            "errorMessage" : "Laita vastaukseksi numero välillä 0-5.", #TODO: add 'peruuta kirjoittamalla alkuun' tms
            "validation_func": scoring.liikunta_validate_intensity,
            "child" : {
                "msg" : "Kuinka kauan liikunta kesti tunteina?",
                "errorMessage" : "Laita oikea tuntimäärä kestoon.",
                "validation_func": scoring.liikunta_validate_duration,
                "child" : {
                    "msg" : "Hieno homma, jatka samaan malliin!", #TODO: good?
                    "score_func": scoring.liikunta_score
                }
            }
        },
        #TODO
        "alkoholi" : {
            #TODO: change this
            "msg": """
            Kuinka rankasti tuli otettua?

Voit tulkita tasoja esim. seuraavasti:
No blast - "Ehkä otin, ehkä en"
Medium blast - "Kun otan, niin juon"
Full blast - tiedät mitä tämä tarkoittaa
Bläkäri - "Vain Bläkkisvuohi muistaa"
            """,
            "errorMessage": BUTTONS_ERROR_MSG,
            "children": OrderedDict([
                ("ei ollenkaan", {
                    "msg": "Hienoa!", # TODO
                    "score_func": lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                #TODO: capitalization?
                ("no blast", {
                    "msg": "Selvä homma.", #TODO
                    "score_func": lambda h: ScoreObject(1, BAD_KEY, h),
                }),
                ("medium blast", {
                    "msg": "Hienosti.", #TODO
                    "score_func": lambda h: ScoreObject(2, BAD_KEY, h),
                }),
                ("full blast", {
                    "msg": "Hienosti.", #TODO
                    "score_func": lambda h: ScoreObject(3, BAD_KEY, h),
                }),
                ("bläkäri", {
                    "msg": "Hienosti.", #TODO
                    "score_func": lambda h: ScoreObject(4, BAD_KEY, h),
                }),
             ]),
        },
        "ruoka" : {
            "msg" : "Miten hyvin söit tänään?",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("panostin tänään",  {
                    "msg" : "Hienoa.",          #TODO
                    "score_func" : lambda h: ScoreObject(1, GOOD_KEY, h),
                }),
                ("normipäivä", {
                    "msg" : "Hienosti.",        #TODO
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("huonosti", {
                    "msg" : "Hienosti.",        #TODO
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h),
                }),
            ]),
        },
        "vapaa-aika" : {
            "msg" : "Kuinka paljon vietit vapaa-aikaa tänään?",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("runsaasti", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(2, GOOD_KEY, h),
                }),
                ("sopivasti", {
                    "msg" : "Hienosti",         #TODO
                    "score_func" : lambda h: ScoreObject(1, GOOD_KEY, h),
                }),
                ("vähän", {
                    "msg" : "Hienosti",         #TODO
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
                ("ei riittävästi", {
                    "msg" : "Hienosti",          #TODO
                    "score_func" : lambda h: ScoreObject(1, BAD_KEY, h),
                }),
            ]),
        },
        "stressi" : {
            "msg" : "Kuinka stressaantunut olet ollut tänään?",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("paljon", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(-2, BAD_KEY, h),
                }),
                ("vähän", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(-1, BAD_KEY, h),
                }),
                ("ei lainkaan", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(0, GOOD_KEY, h),
                }),
            ]),
        },
        "uni" : {
            "msg" : "Miten hyvin nukuit tänään?",
            "errorMessage" : BUTTONS_ERROR_MSG,
            "children" : OrderedDict([
                ("tosi hyvin", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(2, GOOD_KEY, h),
                }),
                ("riittävästi", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(1, GOOD_KEY, h),
                }),
                ("huonosti", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(-1, BAD_KEY, h,)
                }),
                ("heräsin darrassa", {
                    "msg" : "Hienosti.",
                    "score_func" : lambda h: ScoreObject(-2, BAD_KEY, h),
                }),
            ]),
        },
    },
    #TODO: /lisaaMonta is a special case, handle it...
    "root": True
}

def verifyTree(tree, verbose = False):
    """
    recursively traverse the message tree and check that each node has certain attributes
    """

    if tree != STRING_TREE:
        # every other node than the root should have 'msg'
        assert "msg" in tree, tree
    #assert "errorMessage" in tree, tree # needed? -- TODO: this is needed only for nodes with children, move it accordingly.

    if "score_func" in tree:
      assert type(tree["score_func"]) == types.FunctionType

    if "children" in tree:
        for childName, child in tree["children"].items():
            verifyTree(child, verbose)

    elif "child" in tree:
        assert "validation_func" in tree
        verifyTree(tree["child"], verbose)

    else:
        if verbose:
            print("verifyTree(): found leaf node: {}".format(tree))
        assert "score_func" in tree, "no score function found for leaf {}".format(tree)

verifyTree(STRING_TREE)

# this error is thrown if a message is invalid in a given context
class InvalidMessageError(Exception): pass


class StringTreeParser():
    def __init__(self):
        self.root = STRING_TREE
        self.current_message = STRING_TREE
        self.message_chain = []

    def goForward(self, message_str): #, user): #TODO
        """
        Attempt to advance the conversation based on message_str. If the
        message is invalid, raise ValueError so the caller can send the
        errorMessage of the current message.
        Returns a pair (next_message, validated_value), where next_message is
        the subtree dict of the rest of the conversation and validated_value is
        the validated value of message_str (such as a number), if applicable,
        or None.
        """
        next_message = None
        validated_value = None

        node = self.current_message
        if "children" in node:
            children = node["children"]

            if message_str not in children:
                #TODO: back button etc
                #if message_str in [RETURN_BUTTON_MESSAGE, RETURN_MESSAGE]: self.reset(); return self.nextMessage #TODO: not good idea to reset here without notifying caller...
                raise InvalidMessageError("invalid button") #TODO: should include errorMessage here?
            else:
                self.message_chain.append(node)
                self.current_message = children[message_str]
                #return self.current_message #TODO: move this to 'ret'?
                next_message = self.current_message

        elif "child" in node:
            # validate message
            validated_value = node["validation_func"](message_str)
            if validated_value is None:
                raise InvalidMessageError("invalid value")
            else:
                self.message_chain.append(node)
                self.current_message = node["child"]
                #return self.current_message
                next_message = self.current_message

        # was leaf, don't do anything? is it good that the caller handles no children?
        if "score_func" in node:
            print("TODO: score_func found, what do???") #TODO - or should be done by callee?

        return (next_message, validated_value)

        return ret

    def goBack(self):
        if self.message_chain:
            self.current_message = self.message_chain.pop()
        else:
            raise NotImplementedError

    def reset(self):
        self.current_message = self.root
        self.message_chain = []

    def is_at_root(self):
        return self.current_message == self.root
