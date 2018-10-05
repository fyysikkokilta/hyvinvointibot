import sys
import time
import re
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove

from stringtree import STRING_TREE, StringTreeParser
from stringtree import GROUP_REPLY_MESSAGE, DID_NOT_UNDERSTAND_MESSAGE
from stringtree import InvalidMessageError

# globals, might be defined in functions
BOT_TIMEOUT = 5 * 60 # 5 minutes
BOT_TOKEN = None
BOT_USERNAME = None

# TODO: replace with real database
from collections import defaultdict
db = defaultdict(lambda: {"good": 0, "bad": 0}) #TODO: replace magic strings with string constants

class HyvinvointiChat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self.stringTreeParser = StringTreeParser()
        self.current_score_parameters = []

    def on_chat_message(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)

        pprint(msg)
        print("\n")

        is_group = chat_type in ["group", "supergroup"]

        if content_type != "text":
            return
        txt = msg["text"].strip().lower()

        if is_group:
            # see if the message is aimed at us
            if re.match(r"/\w+@{}$".format(BOT_USERNAME), txt):
                self.sender.sendMessage(
                        GROUP_REPLY_MESSAGE,
                        reply_to_message_id = msg["message_id"]
                        )
            # don't do anything else in a group chat
            return

        # we're in a private chat
        command = None
        reply_markup = ReplyKeyboardRemove()
        reply_message_str = None
        end_conversation = False
        if txt.startswith("/"):
            # possibly a command, strip '@username' from the end
            command = txt.split("@")[0]

        if command:
            # first, handle special commands
            if command == "/lisaamonta":
                #TODO: special case
                print("NOT IMPLEMENTED: /lisaamonta")
                return

            # otherwise, treat the command as a regular message and proceed
            self.stringTreeParser.reset()
            self.current_score_parameters = []
            txt = command

        elif self.stringTreeParser.is_at_root():
            # conversation has not been started but the message is not a command
            # TODO: kind of hacky / inconsistent, should maybe use goForward regularly instead?
            self.sender.sendMessage(DID_NOT_UNDERSTAND_MESSAGE, reply_markup = ReplyKeyboardRemove())
            return

        # attempt to continue conversation
        try:
            next_message, validated_value = self.stringTreeParser.goForward(txt)

            if validated_value is not None:
                self.current_score_parameters.append(validated_value)

            reply_message_str = next_message["msg"]

            if "children" in next_message:
                buttons = next_message["children"].keys()
                buttons = list(map(lambda b: b.capitalize(), buttons))
                max_row_length = 3
                buttons_reshaped = []
                for i in range(0, len(buttons), max_row_length):
                    buttons_reshaped.append(buttons[i:i+max_row_length])

                pprint(buttons_reshaped)
                reply_markup = ReplyKeyboardMarkup(keyboard = buttons_reshaped)

            elif "child" not in next_message:
                # is a leaf, stop conversation
                end_conversation = True
                # evaluate score
                if "score_func" in next_message:
                    score_obj = next_message["score_func"](self.current_score_parameters)
                    db[chat_id][score_obj.type] += score_obj.value
                    pprint(db)

        except InvalidMessageError:
            # message was invalid
            # current_message["errorMessage"] should not throw an error if the tree is valid
            cm = self.stringTreeParser.current_message
            reply_message_str = cm["errorMessage"]
            # if there's buttons, don't remove them
            if "children" in cm: reply_markup = None


        if reply_message_str:
            self.sender.sendMessage(
                    reply_message_str,
                    reply_markup = reply_markup)
        else:
            print("reply_message_str was empty, not sure what happened") #TODO: does this ever happen?

        if end_conversation:
            self.close()

def main():
    global BOT_USERNAME

    bot = telepot.DelegatorBot(BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
        )
    ])

    BOT_USERNAME = bot.getMe()["username"].lower()

    #TODO: flush messages

    MessageLoop(bot).run_as_thread()
    print('Listening @{} ...'.format(bot.getMe()["username"]))

    while 1:
        time.sleep(10)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]
    else:
        try:
            with open("token.txt", "r") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        BOT_TOKEN = line.strip()
                        break

        except FileNotFoundError:
            print("bot token not found. please provide it as a command-line argument or in a file 'token.txt'. exiting.")
            sys.exit()

    main()
