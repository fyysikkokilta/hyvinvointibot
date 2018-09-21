STRING_TREE = {
    "msg" : "Mitä olet tehnyt tänään?",
    "buttons" : [["Liikunta", "liikunta_choice"], ["Alkoholi", "alkoholi_choice"]],
    "errorMessage" : "Paina nappia.",                                   #TODO: korjaa
    "children" : {
        "liikunta_choice" : {
            "msg" : "Asteikolla 0-5, kuinka intensiivistä se oli?",
            "errorMessage" : "Laita oikea numero intensiteetiksi.",     #TODO: korjaa
            "child" : {
                "msg" : "Kuinka kauan liikunta kesti tunteina?",
                "errorMessage" : "Laita oikea numero kestoon.",         #TODO: korjaa
                "child" : {
                    "msg" : "Hieno homma, jatka samaan malliin!"        #TODO: korjaa

                }
            }
        }
    }
}
# class ReplyMessage():
#     def __init__(self):
#         pass

# class ReplyMessageWithChoices(ReplyMessage):
#     def __init__(self, children):
#         super(ReplyMessageWithChoices, self).__init__()
#         self._children = children

class StringTreeParser():
    def __init__(self):
        self.root = STRING_TREE
        self.current_message = STRING_TREE
        self.message_chain = []

    def goForward(self, message_str):
        ret = None

        try:
            button_id = message_str
            child = self.current_message["children"][button_id]
            
            ret = child


            #buttons = current_message["buttons"].filter(lambda x: x[1] == button_id)    
        except ValueError:
            pass
        #was not a button, check for number
        try:
            number = float(message_str)


        except ValueError:
            pass
        #was not a number, return error message

        if (ret == None):
            ret = {"msg" : "Tapahtui virhe. Hienosti."}
        
        ret.setDefault("buttons", None)

        self.message_chain.append(ret)
        self.current_message = ret

        return ret

        reply = self.current_message["msg"]
        self.message_chain.append(self.current_message)
        self.current_message = reply

        #return list(reply.keys())
        if type(reply) == str:
            return reply
        else:
            assert type(reply) == dict
            return list(reply.keys())[0]

    def go_back(self):
        if self.message_chain:
            self.current_message = self.message_chain.pop()
