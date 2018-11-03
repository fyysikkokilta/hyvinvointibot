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

  #for p in participants.find(): # dbm version
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
  alcohol = defaultdict(lambda: defaultdict(int))

  sports_hours = []
  n_well_slept_nights = 0

  #for p in participants.find(): # dbm version
  for p in participants:
      h = p["history"]
      #h_stress = [x for x in h if x["category"] == "stressi"]
      for entry in h:
        dow = (datetime.datetime.fromtimestamp(entry["timestamp"]).weekday() - 1) % 7
        if entry["category"] == "stressi":
          stress[dow][entry["params"][0]] += 1
        elif entry["category"] == "alkoholi":
          alcohol[dow][entry["params"][0]] += 1
        elif entry["category"] == "liikunta" and entry["params"][0] > 0:
          #total_sports_hours += entry["params"][1]
          sports_hours.append(entry["params"][1])
        elif entry["category"] == "uni" and entry["params"][0] == "tosi hyvin":
          n_well_slept_nights += 1

  n_participants = len(participants)
  sports_hours = np.array(sports_hours)
  total_sports_hours = sum(sports_hours)

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

def plot_alcohol_multihist():
  fig = plt.figure()
  ax = fig.gca()

  alc1 = np.array([x["no blast"] for x in alcohol.values()])
  alc2 = np.array([x["medium blast"] for x in alcohol.values()])
  alc3 = np.array([x["full blast"] for x in alcohol.values()])
  alc4 = np.array([x["bläkäri"] for x in alcohol.values()])
  days = np.arange(7) * 2

  days_labels = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
  alcohol_labels = ['No blast', 'Medium blast', "Full blast", 'Bläkäri']

  bar_w = 0.4

  ax.bar(days - 1.5*bar_w, alc1, width = bar_w, label = alcohol_labels[0], align = "center")
  ax.bar(days - 0.5*bar_w, alc2, width = bar_w, label = alcohol_labels[1], align = "center")
  ax.bar(days + 0.5*bar_w, alc3, width = bar_w, label = alcohol_labels[2], align = "center")
  ax.bar(days + 1.5*bar_w, alc4, width = bar_w, label = alcohol_labels[3], align = "center")
  #ax.bar(days        , stress2 + stress3, width = bar_w)

  ax.set_ylabel("Merkintöjen lkm")

  ax.set_xticks(days)
  ax.set_xticklabels(days_labels)
  #ax.set_ylim([0, 120])

  leg = ax.legend()
  leg.set_draggable(True)

  ax.set_title("Alkoholimerkinnät eri viikonpäiville")

#plot_stress_multihist()
#plot_alcohol_multihist()

# mielen kiintoisia faktoja
print("total sports hours: {} (variance {})".format(total_sports_hours, np.var(sports_hours)))
print("total blackouts: {}".format(sum([x["bläkäri"] for x in alcohol.values()])))
print("no. of well slept nights: {}".format(n_well_slept_nights))

plt.show(block = not ipython)
