"""
DBManager is a thin wrapper around PyMongo
"""

from pymongo import MongoClient

from scoring import GOOD_KEY, BAD_KEY

DATABASE_NAME = "hyvinvointi-2018-test" #TODO: remove -test
HISTORY_KEY = "history"

def parse_teams_and_add_to_db(filename):
    #TODO
    # read teams from a text file and store them in the dict 'db'

    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line and line.startswith("#"):
                continue

            s = list(map(lambda p: p.strip(), line.split(";")))
            team_name = s[0]
            for uname in s[1:]:
                ??? #TODO

class DBManager():
    def __init__(self):
        self.connection = MongoClient()
        self.db = self.connection[DATABASE_NAME]
        self.participants = self.db.participants

    def insert_score(self, username, score_obj):
        """
        Add the information of the score objec to the user
        """
        user_data = self.participants.find_one({"username": username})
        if user_data is None:
            print("user_data is None")
            #self.participants.insert_one( ... )
            return
        user_data[score_obj.type] += score_obj.value
        user_data[HISTORY_KEY].append(score_obj.history)

    def get_history(self, username):
        raise NotImplementedError

    def get_top_lists(self):
        """
        Return the list of the top 10 (?) most good and most bad teams, sorted
        according to their score
        """

        raise NotImplementedError


if __name__ == "__main__":
