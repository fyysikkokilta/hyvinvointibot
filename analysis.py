import json
#import dbmanager
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import datetime
from collections import defaultdict, OrderedDict

"""
Plot/statistics ideas:
  - multi-histogram of stress as a function of weekday
  - -||- of alkoholi as a function of weekday
  - cumulative hyvinvointi, pahoinvointi, hyv - pah points
  - average hours of liikunta / user

 (- paras yksittäinen suoritus liikuntatunnit yhteenlaskettuna)
  - jokaiselle joukkueelle hyvin/pahoinvoivin yksittäinen päivä

  - stressaantunein / dokatuin / parhaiten syönyt / parhaiten nukkunut tms tiimi
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

  #data_filename = "database-export.json"
  data_filename = "database-export-2018-11-12-111740.json"
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

  team_scores = {"good": defaultdict(list), "bad": defaultdict(list)}
  team_scores_timestamps = {"good": defaultdict(list), "bad": defaultdict(list) }
  teams = defaultdict(set)

  stress = defaultdict(lambda: defaultdict(int))
  alcohol = defaultdict(lambda: defaultdict(int))
  teams_alcohol = defaultdict(lambda: defaultdict(int))
  teams_food = defaultdict(lambda: defaultdict(int))

  sports_hours = []
  n_well_slept_nights = 0

  daily_points = {"good": defaultdict(float), "bad": defaultdict(float)}
  daily_participants = {"good": defaultdict(set), "bad": defaultdict(set)}

  #for p in participants.find(): # dbm version
  for p in participants:
      h = p["history"]

      team = p["team"]

      for entry in h:
        d = datetime.datetime.fromtimestamp(entry["timestamp"]).date()
        dow = (d.weekday() - 1) % 7
        if entry["category"] == "stressi":
          stress[dow][entry["params"][0]] += 1
        elif entry["category"] == "alkoholi":

          blast = entry["params"][0]
          alcohol[dow][blast] += 1

          teams_alcohol[team][blast] += 1

        elif entry["category"] == "liikunta" and entry["params"][0] > 0:

          sports_hours.append(entry["params"][1])

        elif entry["category"] == "uni" and entry["params"][0] == "tosi hyvin":

          n_well_slept_nights += 1

        elif entry["category"] == "ruoka":
          teams_food[team][entry["params"][0]] += 1

        kind = entry["type"]
        value = entry["value"]
        team_scores[kind][team].append(value)
        team_scores_timestamps[kind][team].append(d)

        uname = p["username"]
        teams[team].add(uname)

        daily_points[kind][d] += value
        daily_participants[kind][d].add(uname)

  n_participants = len(participants)
  team_sizes = dict(map(lambda x: (x[0], len(x[1])), teams.items()))

  def rescale_points(point_list, team_name): return sum(point_list) * 10.0 / team_sizes[team_name]

  def get_rankings(kind):
    scores = team_scores[kind].items()
    scores = map(lambda x: (x[0], rescale_points(x[1], x[0])), scores)
    scores = list(scores)
    scores.sort(key = lambda x: -x[1])
    return OrderedDict(scores)

  rankings = {
      "good": get_rankings("good"),
      "bad": get_rankings("bad"),
  }
  rankings["sum abs"] = OrderedDict(sorted(
      [(name, rankings["good"][name] + rankings["bad"][name]) for name in team_sizes.keys()],
      key = lambda x: -x[1]
      ))
  rankings["diff"] = OrderedDict(sorted(
      [(name, rankings["good"][name] - rankings["bad"][name]) for name in team_sizes.keys()],
      key = lambda x: -x[1]
      ))

  sports_hours = np.array(sports_hours)
  total_sports_hours = sum(sports_hours)

  daily_counts = {}
  for kind in ["good", "bad"]:
    daily_counts[kind] = dict(
        map(lambda x: (x[0], len(x[1])),
          daily_participants[kind].items()
        ))

  alcohol_weights = {
      "ei ollenkaan!" : 0, "no blast": 1, "medium blast": 2,
      "full blast": 3, "bläkäri": 4
      }

  most_dokattu = max(teams_alcohol.items(),
      key = lambda x: sum([alcohol_weights[y[0]] * y[1] for y in x[1].items()]) / team_sizes[x[0]]
      )

  least_dokattu = max(teams_alcohol.items(),
      key = lambda x: x[1]["ei ollenkaan!"] / team_sizes[x[0]]
      )

  food_weights = {
      "huonosti": 0,
      "normipäivä": 0,
      "tavallista paremmin": 1,
      "panostin tänään": 2,
      }

  best_food = max(teams_food.items(),
      key = lambda x: sum([food_weights[y[0]] * y[1] for y in x[1].items()]) / team_sizes[x[0]]
      )

  analysis_done = True

def plot_stress_multihist():
  #{{{
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
  #}}}

def plot_alcohol_multihist():
  #{{{
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
  #}}}

def plot_team_cumulative_points():
  #{{{

  fig = plt.figure()
  ax = fig.gca()

  for t in teams:
    for kind in ["bad"]: #["good", "bad"]:
      points_g = np.array(team_scores[kind][t])
      ts_g = np.array(team_scores_timestamps[kind][t])

      ts_g_u, ts_g_i = np.unique(ts_g, return_inverse = True)

      points_g_u = np.zeros_like(ts_g_u)

      for i, p in enumerate(points_g):
        points_g_u[ts_g_i[i]] += p

      ts_sort_i = np.argsort(ts_g_u)
      ts_g_u = ts_g_u[ts_sort_i]
      points_g_u[ts_sort_i] = points_g_u

      points_g_u /= 1.0 * team_sizes[t]

      ax.plot(ts_g_u, np.cumsum(points_g_u), label = t)
      #ax.plot(ts_g_u, points_g_u, label = t)

  leg = ax.legend()
  leg.set_draggable(True)
  #}}}

def plot_average_daily_points():

  fig = plt.figure()
  ax = fig.gca()

  t_good = []
  y_good = []

  t_bad = []
  y_bad = []

  for k, v in daily_points["good"].items():
    t_good.append(k)
    y_good.append(v / daily_counts["good"][k])

  for k, v in daily_points["bad"].items():
    t_bad.append(k)
    y_bad.append(v / daily_counts["bad"][k])

  t_good = np.array(t_good)
  y_good = np.array(y_good)
  good_sort_i = np.argsort(t_good)
  t_good = t_good[good_sort_i]
  y_good = y_good[good_sort_i]

  t_bad = np.array(t_bad)
  y_bad = np.array(y_bad)
  bad_sort_i = np.argsort(t_bad)
  t_bad = t_bad[bad_sort_i]
  y_bad = y_bad[bad_sort_i]

  ax.plot(t_good + datetime.timedelta(days = -1), y_good, marker = "x")
  ax.plot(t_bad + datetime.timedelta(days = -1), y_bad, marker = "x")

#plot_stress_multihist()
#plot_alcohol_multihist()
#plot_team_cumulative_points()
#plot_average_daily_points()

# mielen kiintoisia faktoja
print("total sports hours: {} (variance {})".format(total_sports_hours, np.var(sports_hours)))
print("total blackouts: {}".format(sum([x["bläkäri"] for x in alcohol.values()])))
print("full blast count: {}".format(sum([x["full blast"] for x in alcohol.values()])))
print("no blast count: {}".format(sum([x["no blast"] for x in alcohol.values()])))
print("ei ollenkaan count: {}".format(sum([x["ei ollenkaan!"] for x in alcohol.values()])))
print("no. of well slept nights: {}".format(n_well_slept_nights))
print("\nmost dokattu:"); pprint(most_dokattu)
print("\nleast dokattu:"); pprint(least_dokattu)
print("\npahimmat tissuttelijat:"); pprint(max(teams_alcohol.items(), key = lambda x: x[1]["no blast"]))
print("\nbest food:"); pprint(best_food)

def print_rankings(kind):
  for (name, score) in rankings[kind].items():
    print("{} - {:.2f}".format(name, score))

print("\n"); print("RANKINGS:\n");
print("Hyvinvointi:\n");  print_rankings("good");    print("\n")
print("Pahoinvointi:\n"); print_rankings("bad");     print("\n")
print("sum abs:\n");      print_rankings("sum abs"); print("\n")
print("diff:\n");         print_rankings("diff");

plt.show(block = not ipython)

# vim: set fdm=marker :
