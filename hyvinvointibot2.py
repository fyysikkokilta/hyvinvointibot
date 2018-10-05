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
from stringtree import INVALID_COMMAND_MESSAGE

# globals, might be defined in functions
BOT_TIMEOUT = 5 * 60 # 5 minutes
BOT_TOKEN = None
BOT_USERNAME = None

class HyvinvointiChat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self.stringTreeParser = StringTreeParser()

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
        if txt.startswith("/"):
            # possibly a command, strip '@username' from the end
            command = txt.split("@")[0]

        if command:
            if command == "/lisaa":
                self.stringTreeParser.reset()
                print("NOT IMPLEMENTED: /lisaa")
                return # ?
            elif command == "/lisaamonta":
                print("NOT IMPLEMENTED: /lisaaMonta")
                return # ?
            else:
                # was a command but an invalid command
                self.sender.sendMessage(INVALID_COMMAND_MESSAGE)
                return

        # not a command, try to continue conversation
        if not self.stringTreeParser.is_at_root():

            print("would continue conversation")
            return

        else:
            self.sender.sendMessage(DID_NOT_UNDERSTAND_MESSAGE)
            return



        #bot_username =

        #if chat_type != "private":
        #    print("TODO: should send a reply along the lines of 'lisää tapahtumia yksityisviestillä', not implemented yet") #TODO
        #    return

        #reply = None
        #reply_markup = None

        #pprint(msg)

        #if msg["text"] == "aloita":

        #    # TODO: good idea to always reset on /start command? (probably yes)
        #    self.stringTreeParser.reset()
        #    cm = self.stringTreeParser.current_message
        #    reply = cm["msg"]

        #    # NOTE: assuming that the first choice always has buttons.
        #    reply_markup = ReplyKeyboardMarkup(keyboard = [cm["buttons"]])

        #    #self.sender.sendMessage

        #else:
        #    #TODO: check that we're in the middle of a conversation
        #    #if not self.stringTreeParser.is_at_root(): return # or something

        #    try:
        #        user = chat_id # this is fine since we're not in a group chat
        #        next_msg = self.stringTreeParser.goForward(msg["text"], user)
        #        reply = next_msg["msg"]
        #        if "buttons" in next_msg:
        #            reply_markup = next_msg["buttons"]
        #        else:
        #            reply_markup = ReplyKeyboardRemove()
        #        #TODO
        #        #if not "children" in next_msg:
        #        #    ... call self.close() after 


        #    except ValueError:
        #        #TODO: what should be done here?
        #        #nest_msg = self.stringTreeParser.current_message["error_msg"] ???
        #        pass


        #if reply:
        #    self.sender.sendMessage(reply, reply_markup = reply_markup)
        #else:
        #    print("not replying to")
        #    pprint(msg)

def main():
    global BOT_USERNAME

    bot = telepot.DelegatorBot(BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
        )
    ])

    BOT_USERNAME = bot.getMe()["username"].lower()

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
