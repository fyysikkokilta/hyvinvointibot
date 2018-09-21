# -*- coding: utf-8 -*-

import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space

BOT_TIMEOUT = 5 * 60 # 5 minutes

"""
Counts number of messages a user has sent. Starts over if silent for 10 seconds.
Illustrates the basic usage of `DelegateBot` and `ChatHandler`.
"""

class HyvinvointiChat(telepot.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self._count = 0

        #self._state = ???

    def on_chat_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)


TOKEN = "508674817:AAEOm7RVU64DB1733Xz7VCQ71cgjmpr9EoE"

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, HyvinvointiChat, timeout=BOT_TIMEOUT
    ),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)
