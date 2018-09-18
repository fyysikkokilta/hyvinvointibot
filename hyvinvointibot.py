# -*- coding: utf-8 -*-

import telepot, telepot.loop
# https://github.com/nickoala/telepot/blob/master/examples/simple/skeleton_route.py
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup
import time
import __main__
from collections import defaultdict

BOT_API_TOKEN = "508674817:AAEOm7RVU64DB1733Xz7VCQ71cgjmpr9EoE" # @KeijoBot

points = defaultdict(dict)

def handle_message(msg):
  global bot

  #print(msg)

  content_type, chat_type, chat_id = telepot.glance(msg)
  timestamp = time.strftime("%d.%m. %H:%M:%S")
  frm = msg["from"]

  is_group = chat_type in ["group", "supergroup"]

  uname = None
  try:
    uname = frm["username"]
  except KeyError:
    pass

  try:
    txt = msg["text"]
    txt = txt.lower()
    #TODO: if applicable: filter out edits
    #msg["edit_date"] # this raises a KeyError if the message is an edit (?)
  except KeyError:
    # If the message wasn't text, don't do anything.
    return

  sent = False

  if txt == "/lisaa":
    markup = ReplyKeyboardMarkup(keyboard = [
      ["foo", "bar", "foobar"],
      ["baz", "3"],
      ["back"]
      ])
    bot.sendMessage(chat_id, "asd", reply_markup = markup)
    sent = True

  if sent:
    # log where messages are going
    f = msg["from"]
    first = last = uname = ""
    try:
      first = f["first_name"]
    except KeyError:
      pass
    try:
      last = f["last_name"]
    except KeyError:
      pass
    try:
      uname = f["username"]
    except KeyError:
      pass

    print("{} sent message to {} {} ({}), chat ID {}".format(timestamp, first, last, uname, chat_id))


def on_callback_query(msg):
  print("callback query: {}".format(msg))

def flush_messages(bot):
  updates = bot.getUpdates()
  while updates:
    print("Flushing {} messages.".format(len(updates)))
    # we assume that between here there's been no messages...
    time.sleep(1)
    updates = bot.getUpdates(updates[-1]["update_id"] + 1)

# don't start the tg bot if the scipt is run from an interpreter.
if __name__ == "__main__" and hasattr(__main__, "__file__"):

  bot = telepot.Bot(BOT_API_TOKEN)
  flush_messages(bot)

  telepot.loop.MessageLoop(bot,
      {
        "chat": handle_message,
        "callback_query": on_callback_query,
      }).run_as_thread()

  print("Listening...")
  while True:
    time.sleep(10)
