import sys
import time, datetime
import re
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove

from strings import StringTreeParser, InvalidMessageError
from strings import GROUP_REPLY_MESSAGE, DID_NOT_UNDERSTAND_MESSAGE
from strings import START_ADD_EVENT_MESSAGE, UNKNOWN_COMMAND_MESSAGE
from strings import HELP_MESSAGE, RETURN_BUTTON_MESSAGE, RETURN_MESSAGE
from strings import USER_HISTORY_MESSAGE, NO_USER_HISTORY_MESSAGE
from strings import USER_HISTORY_COUNT_ERROR_MESSAGE, ITEM_REMOVED_SUCCESS_MESSAGE
from strings import USER_HISTORY_COUNT_PROMPT, ALL_ITEMS_ADDED_FOR_TODAY_MESSAGE
from strings import ADDING_MANY_FINISHED_MESSAGE, NOT_PARTICIPANT_MESSAGE
from strings import ADDING_MANY_CANCEL_MESSAGE, ADDING_MANY_CANCELING_MESSAGE
from strings import ADDING_MANY_START_MESSAGE, ITEM_ALREADY_ADDED_FOR_TODAY_MESSAGE
from strings import RANK_MESSAGE, INFO_MESSAGE

from scoring import GOOD_KEY, BAD_KEY

from dbmanager import DBManager, TEAM_KEY, MEMBER_COUNT_KEY
from utils import is_today

# globals, might be defined in functions
BOT_TIMEOUT = 5 * 60 # 5 minutes
BOT_TOKEN = None
BOT_USERNAME = None

# update points every this many hours
UPDATE_POINTS_INTERVAL_H = 4

#TODO: here's a list of larger scale TODO's / goals
"""
TODOx: database
    x teams ~~ done
    x remove entries - done
    x show rankings -- done
        x score index: divide by first position x 100
        x show pahoinvointi in reverse order(?)
TODOx: /lisaapaiva -- DONE
TODOx: /rank -- done
TODOx: all conversation paths -- done
TODOx: score functions -- done
TODOx: back button to all 'button' conversations ~ done
TODOx: prevent duplicates of the event for the same day ~ done
TODOx: merge to master, remane hyvivointibot2 -> hyvinvointibot, stringtree -> strings -- done
TODOx: /aboutme (?): show info about me (team, username, history, team members?) ~~ done
    - team info (show members for a given team), show ranking + index ? -- done
TODO: hottiksen tapahtumat???
    - only possible to add them after the event?
TODOx: /info command - "/info alkoholi" - show info about alcohol (?) -- not gonna do
TODO: BOT_ADMIN constant
TODOx: update scores only once per day ~~ done

bugs / feature requests / feedback:
idea: /poista -> allow replacing entry directly
idea: update /rank results only once per day (how?)
idea/feedback: different message for different values of liikunta numeric value?
"""

dbm = DBManager()

# pretty spaghetti way of keeping track of what we're doing
STATE_ADDING_EVENT = "adding event"
STATE_ADDING_MANY_EVENTS = "adding many events"
STATE_REMOVING_EVENT = "removing event"
STATE_NONE = "none"

class HyvinvointiChat(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(HyvinvointiChat, self).__init__(*args, **kwargs)
        self.stringTreeParser = StringTreeParser()
        self.current_score_parameters = []
        self.state = STATE_NONE
        self.events_to_add_for_today = []

    def on_close(self, x):
        # does something have to be done here?
        pass

    def on_chat_message(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)

        #pprint(msg)
        #print("\n")

        is_group = chat_type in ["group", "supergroup"]

        if content_type != "text":
            return

        txt = msg["text"].strip().lower()

        # some info for debugging
        #if "username" in msg["from"] and msg["from"]["username"].lower() == "target_username":
        #if "/info" in txt:
        if True:
            print(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                txt,
                msg["from"])

        if is_group:
            # see if the message is aimed at us
            if re.match(r"/\w+@{}$".format(BOT_USERNAME), txt):

                # hairy hat command parsing
                command = txt.split("@")[0]

                if command == "/rank":
                    self.send_rankings()
                else:
                    self.sender.sendMessage(
                            GROUP_REPLY_MESSAGE,
                            reply_to_message_id = msg["message_id"]
                            )

            # don't do anything else in a group chat
            self.close()
            return

        ## at this point, we're in a private chat. ##

        # check if the user is a participant (all participants should have a username)
        if "username" not in msg["from"] or not dbm.is_participant(msg["from"]["username"]):
            self.sender.sendMessage(NOT_PARTICIPANT_MESSAGE)
            return

        username = msg["from"]["username"]
        command = None
        #reply_markup = ReplyKeyboardRemove()
        reply_markup = None
        reply_message_str = None
        end_conversation = False
        if txt.startswith("/"): #TODO: consider using telepot features, msg["entities"] has 'bot_command'
            # possibly a command, strip '@username' from the end
            command = txt.split("@")[0]

        if command:

            self.state = STATE_NONE

            if command == "/lisaapaiva":
                categories = self.stringTreeParser.get_categories()
                already_added = dbm.get_todays_history(username)
                already_added = list(map(lambda x: x["category"], already_added))
                to_add = [cat for cat in categories if cat not in already_added]

                if not to_add:
                    self.sender.sendMessage(ALL_ITEMS_ADDED_FOR_TODAY_MESSAGE,
                            reply_markup = ReplyKeyboardRemove())

                    end_conversation = True

                else:
                    self.state = STATE_ADDING_MANY_EVENTS
                    self.events_to_add_for_today = to_add[1:]
                    self.sender.sendMessage(ADDING_MANY_START_MESSAGE)
                    self.add_event_continue_conversation(msg, start_from = to_add[0])

            elif command == "/lisaa":
                self.state = STATE_ADDING_EVENT
                self.add_event_continue_conversation(msg, start_from = "root")

            elif command == "/poista":
                self.state = STATE_REMOVING_EVENT
                end_conversation = self.remove_item_continue_conversation(msg, 0)

            elif command == "/rank":
                self.send_rankings()
                end_conversation = True

            elif command == "/info":
                self.send_info(username)
                end_conversation = True

            elif command == "/help" or command == "/start":
                self.sender.sendMessage(HELP_MESSAGE)

            else:
                self.sender.sendMessage(UNKNOWN_COMMAND_MESSAGE)

        elif self.state == STATE_ADDING_EVENT:
            if txt in [RETURN_MESSAGE.lower(), RETURN_BUTTON_MESSAGE.lower()]:
                self.add_event_continue_conversation(msg, start_from = "root")

            elif txt == ADDING_MANY_CANCEL_MESSAGE.lower():
                self.sender.sendMessage(ADDING_MANY_CANCELING_MESSAGE,
                        reply_markup = ReplyKeyboardRemove())
                end_conversation = True

            else:
                if dbm.has_done_today(username, txt): # hacky...
                    self.sender.sendMessage(ITEM_ALREADY_ADDED_FOR_TODAY_MESSAGE,
                            )
                else:
                    end_conversation = self.add_event_continue_conversation(msg)

        elif self.state == STATE_ADDING_MANY_EVENTS:

            if txt == ADDING_MANY_CANCEL_MESSAGE.lower():
                self.events_to_add_for_today = []
                self.sender.sendMessage(ADDING_MANY_CANCELING_MESSAGE,
                        reply_markup = ReplyKeyboardRemove())
                end_conversation = True

            elif self.events_to_add_for_today:
                if self.add_event_continue_conversation(msg):

                    next_cat = self.events_to_add_for_today.pop(0)

                    self.add_event_continue_conversation(msg,
                            start_from = next_cat)

            else:
                if self.add_event_continue_conversation(msg): # add last event
                    self.sender.sendMessage(ADDING_MANY_FINISHED_MESSAGE,
                            reply_markup = ReplyKeyboardRemove()
                            )
                    end_conversation = True

        elif self.state == STATE_REMOVING_EVENT:
            end_conversation = self.remove_item_continue_conversation(msg, 1)

        else:
            # conversation has not been started but the message is not a command
            self.sender.sendMessage(DID_NOT_UNDERSTAND_MESSAGE, reply_markup = ReplyKeyboardRemove())

        if end_conversation:
            self.state = STATE_NONE
            self.close()


    def add_event_continue_conversation(self, msg, start_from = None):
        """
        Start/continue conversation for adding an event (such as Liikunta or
        Alkoholi). Can be called many times for the /lisaapaiva command. Also
        Handles collecting the parameters needed to calculate the score, and
        storing the score in the database.

        params:
            msg: Telegram message object. assumed to have content_type == "text"
                and a valid username.
            start_from: if not None, start the conversation from here. should
                be either one of stringTreeParser.get_categories() or 'root'
                for restarting. otherwise attempt to continue where we left off
        returns:
            True if the conversation has ended, False otherwise
        """

        reply_markup = None #ReplyKeyboardRemove()
        reply_message_str = None
        end_conversation = False

        txt = msg["text"].strip().lower()
        username = msg["from"]["username"].lower()
        restart = start_from == "root"
        adding_many = self.state == STATE_ADDING_MANY_EVENTS

        try:
            next_message = None
            validated_value = None

            if restart:
                self.stringTreeParser.reset()
                self.current_score_parameters = []
                next_message = self.stringTreeParser.current_message

            elif start_from in self.stringTreeParser.get_categories():

                self.stringTreeParser.reset()
                self.current_score_parameters = []
                next_message, validated_value = self.stringTreeParser.goForward(start_from)

            else:
                # attempt to continue conversation, raises an exception if it fails
                next_message, validated_value = self.stringTreeParser.goForward(txt)

            reply_message_str = next_message["msg"]

            #if adding_many:
            #    reply_message_str += ADDING_MANY_CANCEL_PROMPT

            if validated_value is not None:
                self.current_score_parameters.append(validated_value)
            elif not restart:
                if start_from is None:
                    self.current_score_parameters.append(txt)
                else:
                    self.current_score_parameters.append(start_from)

            if "children" in next_message:
                buttons = self.get_buttons(
                        next_message["children"].keys(),
                        add_return_button = not restart and not adding_many,
                        add_stop_button = True, #adding_many,
                        )
                #pprint(buttons)
                reply_markup = ReplyKeyboardMarkup(keyboard = buttons,
                        resize_keyboard = True,
                        #one_time_keyboard = True,
                        )

            elif "child" not in next_message:
                # we're at a leaf
                end_conversation = True

                # all leaves should have a score function
                #pprint(self.current_score_parameters)
                #TODO: add try-except? might throw an error if there are typos or anything
                score_obj = next_message["score_func"](self.current_score_parameters)
                #pprint(score_obj)

                dbm.insert_score(username, score_obj)

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
            print("ERROR: reply_message_str was empty, not sure what happened") #TODO: does this ever happen?

        return end_conversation


    def get_buttons(self, list_of_strs, add_return_button = True, add_stop_button = False):
        """
        Small helper function for reshaping a list of strings to a 2D array of
        strings with appropriate dimensions.
        """
        max_row_length = 2
        list_of_strs = list(map(lambda b: b.capitalize(), list_of_strs))
        if add_return_button:
            list_of_strs.append(RETURN_BUTTON_MESSAGE)
        if add_stop_button:
            list_of_strs.append(ADDING_MANY_CANCEL_MESSAGE)

        buttons = []
        for i in range(0, len(list_of_strs), max_row_length):
            buttons.append(list_of_strs[i:i+max_row_length])

        return buttons

    def format_user_history(self, hist):
        """
        return the given list of history entries as a nicely formatted string
        """
        hist.sort(key = lambda x: -x["timestamp"]) # sort from new to old
        hist_with_indices = []
        for i, entry in enumerate(hist):
            s = str(i + 1) + " - "
            s += entry["category"].capitalize() + " - "
            s += ", ".join([str(p).capitalize() for p in entry["params"]])
            hist_with_indices.append(s)

        hist_str = "\n".join(hist_with_indices)
        return hist_str

    def remove_item_continue_conversation(self, msg, stage = 0):
        username = msg["from"]["username"]

        txt = msg["text"].lower()

        hist = dbm.get_todays_history(username)
        if not hist:
            self.sender.sendMessage(NO_USER_HISTORY_MESSAGE,
                    reply_markup = ReplyKeyboardRemove())
            return True # end conversation

        if stage == 0:

            hist_str = self.format_user_history(hist)
            reply_str = USER_HISTORY_MESSAGE.format(hist_str)
            reply_str += USER_HISTORY_COUNT_PROMPT
            self.sender.sendMessage(reply_str,
                    reply_markup = ReplyKeyboardRemove())

            return False

        else:
            try:
                n = int(txt)
                if n > len(hist) or n <= 0:
                    raise ValueError

                dbm.remove_nth_newest_event_today(username, n)
                self.sender.sendMessage(ITEM_REMOVED_SUCCESS_MESSAGE)
                return True

            except ValueError:
                self.sender.sendMessage(
                        USER_HISTORY_COUNT_ERROR_MESSAGE.format(len(hist)))

                return False


    def calculate_indexes(self, team_list, good = True):
        """
        calculate the good or bad indexes for team_list, structured as follows:
        [[name1, points], [name2, points], ... ] where points are either good
        or bad points. Also sorts the result
        """
        # this is the score of the leading team, which has an index of 100
        i0 = max(map(lambda x: x[1], team_list))

        if i0 == 0:
            return team_list
        m = 1.0 if good else -1.0
        indexed = list(map(lambda x: [x[0], x[1] / i0 * 100 * m], team_list))
        indexed.sort(key = lambda x: -x[1] * m)
        return indexed

    def point_dict_to_list(self, point_dict, key = GOOD_KEY):
        # key: GOOD_KEY or BAD_KEY
        scale = 10.0
        sgn = 1 if key == GOOD_KEY else -1
        def get_score(x):
            return [x[0], sgn * x[1][key] / x[1][MEMBER_COUNT_KEY] * scale]

        res = list(map(lambda x: get_score(x), point_dict.items()))
        res.sort(key = lambda x: -x[1] * sgn)
        return res

    def send_rankings(self):
        team_points, updated_timestamp = dbm.get_team_points()
        good_list = self.point_dict_to_list(team_points, GOOD_KEY)
        bad_list = self.point_dict_to_list(team_points, BAD_KEY)

        max_no_teams = None
        good_str = "\n".join([
            "*{}* - {} ({:.2f})".format(i + 1, tname, idx)
            for i, (tname, idx) in enumerate(good_list)
            ][:max_no_teams])
        bad_str = "\n".join([
            "*{}* - {} ({:.2f})".format(i + 1, tname, idx)
            for i, (tname, idx) in enumerate(bad_list)
            ][:max_no_teams])

        updated_date_str = datetime.datetime.fromtimestamp(
                updated_timestamp
                ).strftime("%d.%m. %H:%M")

        message_str = RANK_MESSAGE.format(good_str, bad_str, updated_date_str)
        self.sender.sendMessage(message_str,
                reply_markup = ReplyKeyboardRemove(),
                parse_mode = "markdown")

    def send_info(self, username):
        user_data = dbm.get_user_data(username)
        todays_history = dbm.get_todays_history(username)
        team_points, updated_timestamp = dbm.get_team_points()

        team = user_data[TEAM_KEY]
        team_members = ["@" + m for m in dbm.get_team_members(team)]
        n_teams = len(team_points)
        good_list = self.point_dict_to_list(team_points, GOOD_KEY)
        bad_list = self.point_dict_to_list(team_points, BAD_KEY)
        good_idx = next(t[1] for t in good_list if t[0] == team)
        bad_idx = next(t[1] for t in bad_list if t[0] == team)

        team_rank_good = [tname for tname, _ in good_list].index(team) + 1
        team_rank_bad  = [tname for tname, _ in bad_list ].index(team) + 1

        message_str = INFO_MESSAGE.format(
                username = "@" + username,
                team = team,
                team_members = ", ".join(team_members),
                team_rank_good = team_rank_good,
                team_rank_bad = team_rank_bad,
                good_index = good_idx,
                bad_index = bad_idx,
                n_teams = n_teams,
                history_str = self.format_user_history(todays_history),
                )
        #print("send_info(): ", message_str)
        self.sender.sendMessage(message_str) #, parse_mode = "markdown")


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
        _, points_last_updated = dbm.get_team_points()
        t = datetime.datetime.fromtimestamp(time.time())
        t_prev = datetime.datetime.fromtimestamp(points_last_updated)
        #if not is_today(points_last_updated):
        if t.hour != t_prev.hour and (t.hour % UPDATE_POINTS_INTERVAL_H) == 0:
            dbm.update_team_points()
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
