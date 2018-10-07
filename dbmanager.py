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
            score_obj_hist_extended = score_obj.history
            score_obj_hist_extended.extend([score, time.time()])
            user_hist = user_data[HISTORY_KEY]
            user_hist.append(score_obj_hist_extended)

            self.participants.update_one(
                    {USERNAME_KEY : username},
                    {
                        "$inc": {score_obj.type : score},
                        "$set": {HISTORY_KEY : user_hist},
                    })

        except Exception as e:
            print("ERROR: DBManager.insert_score(): {}".format(e))
            return


    def get_history(self, username):
        user_data = self.participants.find_one({USERNAME_KEY : username})
        if user_data is None:
            print("ERROR: DBManager.get_history(): user_data is None for {}".format(username))
            return

        return user_data[HISTORY_KEY] #[-10:] # list is trimmed by callee

    def get_todays_history(self, username):
        history = self.get_history(username)
        return list(filter(lambda x: is_today(x[-1]), history))

    def remove_nth_newest_event_today(self, username, n):
        #user_data = self.participants.find_one({USERNAME_KEY : username})
        #if user_data is None:
        #    print("ERROR: DBManager.remove_nth_newest_event(): user_data is None for {}".format(username))
        #    return

        hist = self.get_todays_history(username)

    def get_top_lists(self, count):
        """
        Return the list of the top `count` most good and most bad teams, sorted
        according to their score
        """
        #TODO: do index calculation here?

        raise NotImplementedError

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
        #TODO: call this function somewhere
        username = username.lower()
        category = category.lower()

        history = self.get_history(username)
        # x[0] should always be the category and x[-1] the timestamp
        filter_func = lambda x: x[0] == category and is_today(x[-1])

        return bool(list(filter(filter_func, history)))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("please provide the name of a text file for parsing as a command line argument.")
        sys.exit()

    parse_teams_and_add_to_db(sys.argv[1])
