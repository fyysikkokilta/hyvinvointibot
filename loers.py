import dbmanager
from pprint import pprint

dbm = dbmanager.DBManager()

# for m in dbm.get_team_members("Sopulisoturit"):
#     print(m)
#     good = 0
#     bad = 0
#     for i in dbm.get_history(m):
#         if i["type"] == "good":
#             good += i["value"]
#         elif i["type"] == "bad":
#             bad += i["value"]
    
#     print(good)
#     print(bad)


participants = dbm.participants

l = list()

for p in participants.find():       #cursor
    username = p["username"]
    good = 0
    bad = 0
    for h in dbm.get_history(username):
        if h["type"] == "good":
            good += h["value"]
        elif h["type"] == "bad":
            bad += h["value"]

    # print(username)
    # print(good)
    # print(bad)

    l.append((username, good, bad))

l = sorted(l, key=lambda name: -name[1]).map(lambda user: (user[0], user[1]+user[2]))
map(lambda user: (user[0], user[1]+user[2]), l)
pprint(l)
