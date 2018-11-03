import json
#import dbmanager
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import datetime 
from collections import defaultdict

"""
Plot/statistics ideas:
  - multi-histogram of stress as a function of weekday
  - -||- of alkoholi as a function of weekday
  - cumulative hyvinvointi, pahoinvointi, hyv - pah points
  - average hours of liikunta / user
"""

plt.close("all")

ipython = False
try:
  get_ipython()
  ipython = True
except:
  pass

#dbm = dbmanager.DBManager()
#participants = dbm.participants

try:
  analysis_done
except NameError:
  analysis_done = False

if not analysis_done or True:
  print("redoing analysis")

  data_filename = "database-export.json"
  with open(data_filename, "r") as f:
    participants = json.loads(f.read())

  scores = list()

  #for p in participants.find():       #cursor
  for p in participants:
      username = p["username"]
      good = 0
      bad = 0
      #for h in dbm.get_history(username):
      for h in p["history"]:
          if h["type"] == "good":
              good += h["value"]
          elif h["type"] == "bad":
              bad += h["value"]

      # print(username)
      # print(good)
      # print(bad)

      scores.append((username, good, bad))

  stress = defaultdict(lambda: defaultdict(int))

  #for p in participants.find():
  for p in participants:
      h = p["history"]
      h_stress = [x for x in h if x["category"] == "stressi"]
      for entry in h_stress:
        dow = (datetime.datetime.fromtimestamp(entry["timestamp"]).weekday() - 1) % 7
        stress[dow][entry["params"][0]] += 1

  analysis_done = True

def plot_stress_multihist():
  fig = plt.figure()
  ax = fig.gca()

  stress1 = np.array([x["en lainkaan"] for x in stress.values()])
  stress2 = np.array([x["vähän"] for x in stress.values()])
  stress3 = np.array([x["paljon"] for x in stress.values()])
  days = np.arange(7)

  days_labels = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
  stress_labels = ["En lainkaan", "Vähän", "Paljon"]

  bar_w = 0.2

  ax.bar(days - bar_w, stress1, width = bar_w, label = stress_labels[0])
  ax.bar(days        , stress2, width = bar_w, label = stress_labels[1])
  ax.bar(days + bar_w, stress3, width = bar_w, label = stress_labels[2])
  #ax.bar(days        , stress2 + stress3, width = bar_w)

  ax.set_ylabel("Merkintöjen lkm")

  ax.set_xticks(days)
  ax.set_xticklabels(days_labels)
  ax.set_ylim([0, 120])

  leg = ax.legend()
  leg.set_draggable(True)

  ax.set_title("Stressimerkinnät eri viikonpäiville")

plot_stress_multihist()

plt.show(block = not ipython)
