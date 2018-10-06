import sys
import time
import re
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove

from stringtree import StringTreeParser, InvalidMessageError
from stringtree import GROUP_REPLY_MESSAGE, DID_NOT_UNDERSTAND_MESSAGE
from stringtree import START_ADD_EVENT_MESSAGE, UNKNOWN_COMMAND_MESSAGE
from stringtree import HELP_MESSAGE

from scoring import GOOD_KEY, BAD_KEY

# globals, might be defined in functions
BOT_TIMEOUT = 5 * 60 # 5 minutes
BOT_TOKEN = None
BOT_USERNAME = None

# TODO: replace with real database
from collections import defaultdict
db = defaultdict(lambda: {GOOD_KEY: 0, BAD_KEY: 0, "history": [], "team": None}) #TODO: replace magic strings with string constants

#TODO: here's a list of larger scale TODO's / goals
"""
TODO: database
    - teams
    - remove entries
TODO: all conversation paths
TODO: score functions
TODO: back button to all 'button' conversations
TODO: hottiksen tapahtumat???
    - only possible to add them after the event?
"""

class HyvinvointiChat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self.stringTreeParser = StringTreeParser()
        self.current_score_parameters = []
        self.adding_event = False

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
        #TODO: check that the sender has a username
        #if "username" not in msg["from"]: ...
        #TODO: check if the user is a participant from the database
        command = None
        reply_markup = ReplyKeyboardRemove()
        reply_message_str = None
        end_conversation = False
        if txt.startswith("/"): #TODO: consider using telepot features, msg["entities"] has 'bot_command'
            # possibly a command, strip '@username' from the end
            command = txt.split("@")[0]

        if command:

            self.adding_event = False # TODO: good idea?

            if command == "/lisaamonta":
                print("NOT IMPLEMENTED: /lisaamonta")
                #self.adding_many_events = True #TODO
                return
            elif command == "/lisaa":
                self.adding_event = True
                self.add_event_continue_conversation(msg, restart = True)

            elif command == "/poista":
                print("NOT IMPLEMENTED: /poista") #TODO

            elif command == "/help":

                self.sender.sendMessage(HELP_MESSAGE)

            else:
                self.sender.sendMessage(UNKNOWN_COMMAND_MESSAGE)

            ## otherwise, treat the command as a regular message and proceed
            #self.stringTreeParser.reset()
            #self.current_score_parameters = []
            #txt = command

        elif self.adding_event:
            #TODO: check if the message was 'alkuun' etc
            #TODO: is end_conversation = continue() correct here?
            end_conversation = self.add_event_continue_conversation(msg)
            if end_conversation:
                self.adding_event = False

        else:
            # conversation has not been started but the message is not a command
            self.sender.sendMessage(DID_NOT_UNDERSTAND_MESSAGE, reply_markup = ReplyKeyboardRemove())

        if end_conversation:
            self.close()


    def add_event_continue_conversation(self, msg, restart = False):
        """
        Start/continue conversation for adding an event (such as Liikunta or
        Alkoholi). Can be called many times for the /lisaaMonta command. Also
        Handles collecting the parameters needed to calculate the score, and
        storing the score in the database.

        params:
            msg: Telegram message object. assumed to have content_type == "text"
                and a valid username.
            restart: restart the conversation
        returns:
            True if the conversation has ended, False otherwise
        """

        reply_markup = ReplyKeyboardRemove()
        reply_message_str = None
        end_conversation = False

        txt = msg["text"].strip().lower()
        uname = msg["from"]["username"]

        try:
            next_message = None
            validated_value = None

            if restart:
                self.stringTreeParser.reset()
                self.current_score_parameters = []
                next_message = self.stringTreeParser.current_message

            else:
                # attempt to continue conversation, raises an exception if it fails
                next_message, validated_value = self.stringTreeParser.goForward(txt)

            reply_message_str = next_message["msg"]

            if validated_value is not None:
                self.current_score_parameters.append(validated_value)
            elif not restart:
                self.current_score_parameters.append(txt)

            if "children" in next_message:
                #self.current_score_parameters.append(txt)
                buttons = self.get_buttons(next_message["children"].keys())
                pprint(buttons) #TODO: remove
                reply_markup = ReplyKeyboardMarkup(keyboard = buttons)

            elif "child" not in next_message:
                # we're at a leaf
                end_conversation = True

                # all leaves should have a score function
                #pprint(self.current_score_parameters) #TODO: remove
                #TODO: add try-except? might throw an error if there are typos or anything
                score_obj = next_message["score_func"](self.current_score_parameters)
                pprint(score_obj)

                db[uname][score_obj.type] += score_obj.value

                score_params_with_date = self.current_score_parameters
                score_params_with_date.append(time.time())
                db[uname]["history"].append(score_params_with_date) #TODO

                pprint(db) #TODO: remove

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

        return end_conversation


    def get_buttons(self, list_of_strs):
        """
        Small helper function for reshaping a list of strings to a 2D array of
        strings with appropriate dimensions.
        """
        max_row_length = 3
        list_of_strs = list(map(lambda b: b.capitalize(), list_of_strs))
        buttons = []
        for i in range(0, len(list_of_strs), max_row_length):
            buttons.append(list_of_strs[i:i+max_row_length])

        return buttons

def flush_messages(bot):
    updates = bot.getUpdates()
    while updates:
        print("Flushing {} messages".format(len(updates)))
        updates = bot.getUpdates(updates[-1]["update_id"] + 1)

def main():
    global BOT_USERNAME

    bot = telepot.DelegatorBot(BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
        )
    ])

    BOT_USERNAME = bot.getMe()["username"].lower()

    flush_messages(bot)

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
