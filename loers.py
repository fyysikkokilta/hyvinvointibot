import dbmanager

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

for p in participants.find():       #cursor
    good = 0
    bad = 0
    for h in dbm.get_history(p):
        if h["type"] == "good":
            good += h["value"]
        elif h["type"] == "bad":
            bad += h["value"]

    print(good)
    print(bad)