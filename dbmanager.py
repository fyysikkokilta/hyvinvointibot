"""
DBManager is a thin wrapper around PyMongo
"""

import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from scoring import GOOD_KEY, BAD_KEY

DATABASE_NAME = "hyvinvointi-2018-test" #TODO: remove -test
HISTORY_KEY = "history"

def parse_teams_and_add_to_db(filename):
    # read teams from a text file and store them in the database
    connection = MongoClient()
    db = connection[DATABASE_NAME]
    participants = db.participants

    # assure that each username gets added only once
    # if the index already exists, this doesn't do anything
    participants.create_index("username", unique = True)

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
                                "team" : team_name,
                                "username" : username,
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
        user_data = self.participants.find_one({"username": username})
        if user_data is None:
            print("ERROR: DBManager.insert_score(): could not find user_data for {}\n".format(username))
            return

        try:
            score = score_obj.value
            user_data[score_obj.type] += score #TODO: this is incorrect -- use update
            hist_plus_timestamp_and_value = score_obj.history
            hist_plus_timestamp_and_value.extend([score, time.time()])
            user_data[HISTORY_KEY].append(hist_plus_timestamp_and_value)

            # ehh, this is probably pretty stupid to bounce the history list around between mem <-> db, but oh well...
            self.participants.update_one({"username": username}, {"$set": user_data})

        except Exception as e:
            print("ERROR: DBManager.insert_score(): {}".format(e))
            return


    def get_history(self, username):
        history = participants.find_one({"username" : username})
        if history is None:
            print("history is None")
            return

        return history[HISTORY_KEY][-10:]

    def get_top_lists(self):
        """
        Return the list of the top 10 (?) most good and most bad teams, sorted
        according to their score
        """

        raise NotImplementedError


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("please provide the name of a text file for parsing as a command line argument.")
        sys.exit()

    parse_teams_and_add_to_db(sys.argv[1])
