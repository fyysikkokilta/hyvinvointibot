import types
import scoring

RETURN_BUTTON_ID = "return_choice"

"""
The STRING_TREE object contains all possible chains of discussion. It is a dict
containing dicts. Each sub-dictionary corresponds to a message. Each dict
should have the following key-value pairs:
    msg - the message the bot sends when at this point in the conversation
    errorMessage - a message that the bot should send when the reply wasn't
        sensible

Furthermore, each non-leaf node should have the attributes
    children - multiple choices, which the user can select from using buttons
    OR
    child AND validation_func - in this case, the user is expected to input
        free-form data, such as a number. this data should be validated using
        the function validation_func, which should return True or False.

If a node has neither of the above, it is assumed to be a leaf node, and the
conversation is terminated after it. A leaf node may have a key-value pair
score_func, which evaluates the score of a given conversation chain.
"""

STRING_TREE = {
    # root has no 'msg' (?)
    "errorMessage": "En ymmärrä komentoa. Käytä jotakin annetuista komennoista tai kokeile /help.",
    "children": {
        "/lisaa": {
            "msg" : "Mitä olet tehnyt tänään?",
            #"buttons" : [["Liikunta", "liikunta_choice"]], #["Alkoholi", "alkoholi_choice"]], #TODO
            #"buttons" : ["Liikunta"], #["Alkoholi", "alkoholi_choice"]], #TODO
            "errorMessage" : "Paina nappia.",                                   #TODO: korjaa
            "children" : {
                #"liikunta_choice" : {
                "Liikunta" : {
                    #"branch" : "liikunta",
                    "msg" : "Asteikolla 0-5, kuinka intensiivistä se oli?",
                    #"buttons" : [["1", "1"], ["2", "3"], ["3", "3"]],
                    "errorMessage" : "Laita oikea numero intensiteetiksi.",     #TODO: korjaa
                    "children" : {
                        "liikunta_choice1" : {
                            #"branch" : "liikunta",
                            "msg" : "Kuinka kauan liikunta kesti tunteina?",
                            #"buttons" : [["1", "1"], ["2", "3"], ["3", "3"]],
                            "errorMessage" : "Laita oikea numero kestoon.",         #TODO: korjaa
                            "children" : {
                                "liikunta_choice2" : {
                                    "msg" : "Hieno homma, jatka samaan malliin!",        #TODO: korjaa
                                    "score_func": scoring.liikunta_score
                                }
                            }
                        }
                    }
                },
                #TODO
                #"Alkoholi" :
            },
        },
        "/help": {
            "msg": "help-komento on vielä kesken lörs"
        },
        #TODO: /lisaaMonta is a special case, handle it...
    },
    "root": True
}

#RETURN_BUTTON_MESSAGE = "« Alkuun"

GROUP_REPLY_MESSAGE = "Lähetä komentoja yksityisviestillä."
DID_NOT_UNDERSTAND_MESSAGE = "En ymmärrä. Käytä jotakin annetuista komennoista tai kokeile /help."
INVALID_COMMAND_MESSAGE = "En ymmärrä komentoa. Käytä jotakin annetuista komennoista tai kokeile /help."


db = {}

def verifyTree(tree, verbose = False):
    """
    recursively traverse a tree and check that each node has certain attributes
    """

    assert "msg" in tree, tree
    #assert "errorMessage" in tree # needed?

    #if "buttons" in tree:
    #    assert "children" in tree, "node with buttons but no children: {}".format(tree)
    #    buttons = tree["buttons"]
    #    for button, buttonId in buttons:
    #        assert buttonId.endswith("_choice"), "{}, {}".format(button, buttonId)
    #        assert buttonId in tree["children"], "no choice found for {} in {} ({})".format(buttonId, tree["msg"], tree)

    if "score_func" in tree:
      assert type(tree["score_func"]) == types.FunctionType

    if "children" in tree:
        for childName, child in tree["children"].items():
            verifyTree(child, verbose)

    elif "child" in tree:
        verifyTree(tree["child"], verbose)

    else:
        if verbose:
            print("verifyTree(): found leaf node: {}".format(tree))
        assert "score_func" in tree, "no score function found for leaf {}".format(tree) #TODO: might not be necessary, e.g. for help etc...


# throw this error if a message is invalid in a given context
class InvalidMessageError(Exception): pass


class StringTreeParser():
    def __init__(self):
        self.root = STRING_TREE
        self.current_message = STRING_TREE
        self.message_chain = []
        #verifyTree(self.root)

    def goForward(self, message_str): #, user): #TODO
        """
        Attempt to advance the conversation based on message_str. If the
        message is invalid, raise ValueError so the caller can send the
        errorMessage of the current message.
        Returns the subtree dict of the rest of the conversation.
        """
        ret = None

        if "children" in self.current_message:
            children = self.current_message["children"]

            if message_str not in children:
                raise InvalidMessageError("invalid button") #TODO: should include errorMessage here?
            else:
                self.message_chain.append(self.current_message)
                self.current_message = children[message_str]
                return self.current_message

        else: return {"msg" : "lors"}

        #try:
        #    button_id = float(message_str)
        #    print("button_id (float): {}".format(button_id))
        ##     if button_id <= 5:
        #    if 0 < button_id <= 5:
        #        if (self.current_message["branch"] == "liikunta"):
        #            #db.update({user, button_id})                #TODO: add to db 
        #            print("\npoints added\n")
        #        childName = list(self.current_message["children"].keys())[0]       #TODO: fix this spaghetti
        #        print("childName: {}".format(childName))
        #        ret = self.current_message["children"][childName]


        #except ValueError as e:
        #    print("ValueError when trying to get children based on number: {}".format(e))

        #    try:
        #        button_id = message_str
        #        print("button_id: " + button_id)


        #        if button_id == RETURN_BUTTON_ID:
        #            #TODO
        #            pass

        #        else:
        #            #child = self.current_message["children"][button_id]
        #            assert len(self.current_message["children"]) <= 1
        #            child = list(self.current_message["children"].values())[0]

        #        ret = child

        #        #buttons = current_message["buttons"].filter(lambda x: x[1] == button_id)
        #    except ValueError as e:
        #        print("ValueError when trying to get children based on button: {}".format(e))
        #        pass
        ##was not a button, check for number
        ##was not a number, return error message

        #if (ret == None):
        #    ret = {"msg" : "Tapahtui virhe. Hienosti."}

        ##ret.setdefault("buttons", None)

        #self.message_chain.append(ret)
        #self.current_message = ret

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
