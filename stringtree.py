RETURN_BUTTON_ID = "return_choice"

STRING_TREE = {
    "msg" : "Mitä olet tehnyt tänään?",
    "buttons" : [["Liikunta", "liikunta_choice"]], #["Alkoholi", "alkoholi_choice"]], #TODO
    "errorMessage" : "Paina nappia.",                                   #TODO: korjaa
    "children" : {
        "liikunta_choice" : {
            "branch" : "liikunta",
            "msg" : "Asteikolla 0-5, kuinka intensiivistä se oli?",
            "buttons" : [["1", "1"], ["2", "3"], ["3", "3"]],
            "errorMessage" : "Laita oikea numero intensiteetiksi.",     #TODO: korjaa
            "children" : {
                "liikunta_choice1" : {
                    "branch" : "liikunta",
                    "msg" : "Kuinka kauan liikunta kesti tunteina?",
                    "buttons" : [["1", "1"], ["2", "3"], ["3", "3"]],
                    "errorMessage" : "Laita oikea numero kestoon.",         #TODO: korjaa
                    "children" : {
                        "liikunta_choice2" : {
                            "msg" : "Hieno homma, jatka samaan malliin!"        #TODO: korjaa
                        }
                    }
                }
            }
        }
    }
}

db = {}

def verifyTree(tree, verbose = False):
    """
    recursively traverse a tree and check that each node has certain attributes
    """

    assert "msg" in tree, tree
    #assert "errorMessage" in tree # needed?

    if "buttons" in tree:
        assert "children" in tree, "node with buttons but no children: {}".format(tree)
        buttons = tree["buttons"]
        for button, buttonId in buttons:
            assert buttonId.endswith("_choice"), "{}, {}".format(button, buttonId)
            assert buttonId in tree["children"], "no choice found for {} in {} ({})".format(buttonId, tree["msg"], tree)

    if "children" in tree:
        for childName, child in tree["children"].items():
            verifyTree(child, verbose)

    elif "child" in tree:
        verifyTree(tree["child"], verbose)

    else:
        if verbose:
            print("verifyTree(): found leaf node: {}".format(tree))


class StringTreeParser():
    def __init__(self):
        self.root = STRING_TREE
        self.current_message = STRING_TREE
        self.message_chain = []
        #verifyTree(self.root)

    def goForward(self, message_str, user):
        ret = None

        try:
            button_id = float(message_str)
            print(button_id)
        #     if button_id <= 5:
            if 0 < button_id <= 5:
                if (self.current_message["branch"] == "liikunta"):
                    #db.update({user, button_id})                #TODO: add to db 
                    print("\npoints added\n")
                childName = list(self.current_message["children"].keys())[0]       #TODO: fix this spaghetti
                print(childName)
                ret = self.current_message["children"][childName]
                

        except ValueError:
        
            try:
                button_id = message_str
                print("button_id:" + button_id)


                if button_id == RETURN_BUTTON_ID:
                    #TODO
                    pass

                else:
                    child = self.current_message["children"][button_id]

                ret = child

                #buttons = current_message["buttons"].filter(lambda x: x[1] == button_id)
            except ValueError:
                pass
        #was not a button, check for number
        #was not a number, return error message

        if (ret == None):
            ret = {"msg" : "Tapahtui virhe. Hienosti."}

        #ret.setdefault("buttons", None)

        self.message_chain.append(ret)
        self.current_message = ret

        return ret

    def go_back(self):
        if self.message_chain:
            self.current_message = self.message_chain.pop()
        else:
            raise NotImplementedError

    def reset(self):
        self.current_message = self.root
        self.message_chain = []
