# coding = utf-8

import sys
import time
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from stringtree import STRING_TREE, StringTreeParser
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)


#BOT_TOKEN = "546681733:AAFRjJKFkmKBfsxfZnqnJcLpCllPX554lyU"         #currently @stikubot
BOT_TIMEOUT = 5 * 60 # 5 minutes

"""
Counts number of messages a user has sent. Starts over if silent for 10 seconds.
Illustrates the basic usage of `DelegateBot` and `ChatHandler`.
"""

class HyvinvointiChatStarter(telepot.helper.ChatHandler): 
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChatStarter, self).__init__(*args, **kwargs)
        #self._count = 0
        self.stringTreeParser = StringTreeParser()


    def on_chat_message(self, msg):
        #self._count += 1
        #self.sender.sendMessage(self._count)

        content_type, chat_type, chat_id = telepot.glance(msg)

        print("\non_chat_message()\n")
        pprint(msg)

        if msg["text"] == "aloita":
            self.sender.sendMessage(
                "Paina haluamaasi kategoriaa aloittaaksesi",
                reply_markup = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="Liikunta", callback_data = "liikunta_choice"),
                    ]]
                )
            )               
            print("\nStarter completed, moving on to callback\n")
        self.close()

class HyvinvointiChat(telepot.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self.stringTreeParser = StringTreeParser()

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor = "callback_query")
        user = from_id

        if query_data != "aloita":     #maybe useless
            print("\non_callback_query()\n")
            pprint(msg)

            next_msg = self.stringTreeParser.goForward(query_data, user)

            reply_markup = None
            if "buttons" in next_msg and next_msg["buttons"] is not None:
                inline_keyboard = []
                for btn in next_msg["buttons"]:
                    inline_keyboard.append(
                            [InlineKeyboardButton(text = btn[0], callback_data = btn[1])]
                    )
                reply_markup = InlineKeyboardMarkup(inline_keyboard = inline_keyboard)

            self.editor.editMessageText(next_msg["msg"], reply_markup = reply_markup)


def main():
    bot = telepot.DelegatorBot(BOT_TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, HyvinvointiChatStarter, timeout=BOT_TIMEOUT
        ),
        pave_event_space()(
            per_callback_query_origin(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
        )
    ])
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
