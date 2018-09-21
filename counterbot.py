# -*- coding: utf-8 -*-

import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from stringtree import StringTree

BOT_TOKEN = "508674817:AAEOm7RVU64DB1733Xz7VCQ71cgjmpr9EoE"
BOT_TIMEOUT = 5 * 60 # 5 minutes

"""
Counts number of messages a user has sent. Starts over if silent for 10 seconds.
Illustrates the basic usage of `DelegateBot` and `ChatHandler`.
"""

class HyvinvointiChat(telepot.helper.ChatHandler): #TODO: should be telepot.helper.CallbackQueryOriginHandler

    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self._count = 0
        self.stringTreeParser = StringTreeParser()


    def on_chat_message(self, msg):
        self._count += 1

        self.sender.sendMessage(self._count)

    def on_callback_query(self, msg):
        query_id, form_id, query_data = telepot.glance(msg, flavor = "callback_query")

        print("\non_callback_query()\n")
        print(msg)

        next_msg = self.stringTreeParser.goForward(query_data)

        reply_markup = None
        if "buttons" in next_msg and next_msg["buttons"] is not None:
            inline_keyboard = []
            for btn in next_msg["buttons"]:
                inline_keyboard.append(
                        [InlineKeyboardButton(text = btn[0], callback_data = btn[1])]
                )
            reply_markup = InlineKeyboardMarkup(inline_keyboard = inline_keyboard)

        self.sender.sendMessage(next_msg["msg"], reply_markup = reply_markup)

bot = telepot.DelegatorBot(BOT_TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
    ),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
