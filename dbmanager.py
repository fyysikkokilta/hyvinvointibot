"""
DBManager is a thin wrapper around PyMongo
"""

import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from utils import is_today

from scoring import GOOD_KEY, BAD_KEY

DATABASE_NAME = "hyvinvointi-2018-test" #TODO: remove -test
HISTORY_KEY = "history"
USERNAME_KEY = "username"
TEAM_KEY = "team"

def parse_teams_and_add_to_db(filename):
    # read teams from a text file and store them in the database
    connection = MongoClient()
    db = connection[DATABASE_NAME]
    participants = db.participants

    # assure that each username gets added only once
    # if the index already exists, this doesn't do anything
    participants.create_index(USERNAME_KEY, unique = True)

    with open(filename, "r") as f:
        print("Adding participants to database {}".format(DATABASE_NAME))
        team_names = []
        for line in f.readlines():
            line = line.strip()
            if line and line.startswith("#"):
                continue

            s = list(map(lambda p: p.strip(), line.split(";")))
            team_name = s[0]
            assert team_name not in team_names, "Error: duplicate team name: {}".format(team_name)
            team_names.append(team_name)
            for username in s[1:]:
                username = username.lower()
                if not username: continue # filter out empty strings if there was a ; at the end
                try:
                    # pretty hacky to use try-except here...
                    result = participants.insert_one(
                            {
                                TEAM_KEY : team_name,
                                USERNAME_KEY : username,
                                GOOD_KEY : 0,
                                BAD_KEY : 0,
                                HISTORY_KEY : [],
                                },
                            )
                    print("added: {} - {}".format(team_name, username))

                except DuplicateKeyError:
                    print("already exists: {} - {}".format(team_name, username))


class DBManager():
    def __init__(self):
        self.connection = MongoClient()
        self.db = self.connection[DATABASE_NAME]
        self.participants = self.db.participants

    def get_user_data(self, username):
        username = username.lower()
        user_data = self.participants.find_one({USERNAME_KEY : username})
        if user_data is None:
            print("ERROR: DBManager.get_user_data(): could not find user_data for {}\n".format(username))
            return None
        return user_data

    def insert_score(self, username, score_obj):
        """
        Add the information of the score object to the user
        """
        username = username.lower()
        user_data = self.participants.find_one({USERNAME_KEY : username})
        if user_data is None:
            print("ERROR: DBManager.insert_score(): could not find user_data for {}\n".format(username))
            return

        try:
            score = score_obj.value
            kind = score_obj.type

            # hardcoded DB schema ...
            history_entry_dict = {
                    "params": score_obj.history[1:],
                    "category": score_obj.history[0],
                    "type": score_obj.type,
                    "value": score_obj.value,
                    "timestamp": time.time(),
                    }

            from pprint import pprint; pprint(history_entry_dict)

            user_hist = user_data[HISTORY_KEY]
            user_hist.append(history_entry_dict)

            self.participants.update_one(
                    {USERNAME_KEY : username},
                    {
                        "$inc": {kind : score},
                        "$set": {HISTORY_KEY : user_hist},
                    })

        except Exception as e:
            print("ERROR: DBManager.insert_score(): {}".format(e))
            return


    def get_history(self, username):
        username = username.lower()
        user_data = self.participants.find_one({USERNAME_KEY : username})
        if user_data is None:
            print("ERROR: DBManager.get_history(): user_data is None for {}".format(username))
            return

        return user_data[HISTORY_KEY] #[-10:] # list is trimmed by callee

    def get_todays_history(self, username):
        history = self.get_history(username)
        return list(filter(lambda x: is_today(x["timestamp"]), history))

    def remove_nth_newest_event_today(self, username, n):
        """
        Remove the 'n'th newest history entry, with one-based indexing, i.e.
        n == 1 for newest item
        """
        if n <= 0:
            print("ERROR: DBManager.remove_nth_newest_event_today(): {} {}".format(username, n))
            return

        hist = self.get_history(username)
        hist.sort(key = lambda x: x["timestamp"]) # sort from old to new, just in case
        hist_today = list(filter(lambda x: is_today(x["timestamp"]), hist))
        if not hist_today:
            print("ERROR: DBManager.remove_nth_newest_event_today(): {} {}: no events today".format(username, n))
            return

        #timestamp_to_remove = hist_today[-n][-1]
        item_to_remove = hist_today[-n]
        timestamp = item_to_remove["timestamp"]
        kind = item_to_remove["type"]
        amount = item_to_remove["value"]

        #from pprint import pprint; pprint(item_to_remove)

        hist = list(filter(lambda x: x["timestamp"] != timestamp, hist))
        self.participants.update_one(
                {USERNAME_KEY: username},
                {
                    "$set": { HISTORY_KEY : hist},
                    "$inc": { kind : -amount},
                })

    def is_participant(self, username):
        username = username.lower()
        c = self.participants.count_documents({USERNAME_KEY : username})

        if c > 1:
            print("DBManager.is_participant(): found {} entries for {}".format(c, username))

        return c >= 1

    def has_done_today(self, username, category):
        """
        Check if the given user has added an event with the given category
        (such as 'liikunta' or 'alkoholi') already today.
        """
        username = username.lower()
        category = category.lower()

        history = self.get_history(username)
        filter_func = lambda x: x["category"] == category and is_today(x["timestamp"])

        return bool(list(filter(filter_func, history)))

    def get_team_members(self, team):
        query_result = self.participants.find(
                { TEAM_KEY : team },
                projection = {USERNAME_KEY: True, "_id": False}
            )
        return list(map(lambda d: d[USERNAME_KEY], query_result))


    def get_team_points(self):
        """
        Returns a dict which contains the good and bad points of each team:
        { teamName: {"good": ..., "bad": ... }, ... }
        """
        aggregate_result = self.participants.aggregate([{
                "$group": {
                    "_id": "$" + TEAM_KEY,
                    GOOD_KEY: {"$sum": "$" + GOOD_KEY},
                    BAD_KEY: {"$sum": "$" + BAD_KEY},
                }
            }])

        ret = {}
        for res in aggregate_result:
            team = res["_id"]
            ret[team] = {GOOD_KEY : res[GOOD_KEY], BAD_KEY : res[BAD_KEY]}

        return ret

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("please provide the name of a text file for parsing as a command line argument.")
        sys.exit()

    parse_teams_and_add_to_db(sys.argv[1])
