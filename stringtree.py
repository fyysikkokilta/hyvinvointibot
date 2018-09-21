STRING_TREE = {
    "Mitä olet tehnyt tänään?" : {
        "Liikunta" : {
            "Asteikolla 0-5, kuinka intensiivistä se oli?" : {
                "Kuinka kauan liikunta kesti tunteina?" : {
                    "Hienosti."
                }
            }
        }
    }
}

class ReplyMessage():
    def __init__(self):
        pass

class ReplyMessageWithChoices(ReplyMessage):
    def __init__(self, children):
        super(ReplyMessageWithChoices, self).__init__()
        self._children = children

class StringTree():
    def __init__(self):
        self.tree = STRING_TREE
        self.current_message = list(STRING_TREE.keys())[0]
        self.message_chain = []

    def get_reply(self, message_str):
        reply = None

        try:
            reply = current_message[message_str]
            self.message_chain.append(self.current_message)
            self.current_message = reply

        except ValueError:
            reply = "asd"

        #return list(reply.keys())
        if type(reply) == str:
            return reply
        else:
            assert type(reply) == dict
            return list(reply.keys())[0]

    def go_back(self):
        if self.message_chain:
            self.current_message = self.message_chain.pop()
