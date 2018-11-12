import json
#import dbmanager
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

  - eniten alkoholipisteitä kerännyt joukkue -- done
  - eniten liikuntapisteitä kerännyt joukkue -- done
  - eniten stressipisteitä kerännyt joukkue -- done
  - eniten / vähiten nukkunut joukkue -- done
  - eniten hyvin/huonosti syönyt joukkue -- done
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

# weights from scoring.py
alcohol_weights = {
    "ei ollenkaan!" : 0, "no blast": 1, "medium blast": 2,
    "full blast": 3, "bläkäri": 4
    }

food_weights = {
    "huonosti": -1,
    "normipäivä": 0.1,
    "tavallista paremmin": 1,
    "panostin tänään": 2,
    }

sleep_weights = {
    "tosi hyvin": 1,
    "riittävästi": 0.2,
    "melko huonosti": -0.5,
    "todella huonosti": -1,
    }

stress_weights = {
    "paljon": 2,
    "vähän": 1,
    "en lainkaan": -0.1,
    }


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
  teams_sleep = defaultdict(lambda: defaultdict(int))
  teams_sports = defaultdict(float)
  teams_stress = defaultdict(lambda: defaultdict(int))
  teams_activity = {"good": defaultdict(int), "bad": defaultdict(int)}

  sports_hours = []
  n_well_slept_nights = 0

  daily_points = {"good": defaultdict(float), "bad": defaultdict(float)}
  daily_participants = {"good": defaultdict(set), "bad": defaultdict(set)}
  daily_alcohol = defaultdict(float)
  daily_blackouts = defaultdict(int)

  #for p in participants.find(): # dbm version
  for p in participants:
      h = p["history"]

      team = p["team"]

      for entry in h:
        d = datetime.datetime.fromtimestamp(entry["timestamp"]).date()
        dow = (d.weekday() - 1) % 7
        if entry["category"] == "stressi":

          amount = entry["params"][0]
          teams_stress[team][amount] += 1
          stress[dow][amount] += 1

        elif entry["category"] == "alkoholi":

          blast = entry["params"][0]
          alcohol[dow][blast] += 1

          teams_alcohol[team][blast] += 1

          daily_alcohol[d] += alcohol_weights[blast]
          if blast == "bläkäri":
            daily_blackouts[d] += 1

        elif entry["category"] == "liikunta":

          teams_sports[team] += entry["value"]

          if entry["params"][0] > 0:
            sports_hours.append(entry["params"][1])

        elif entry["category"] == "uni":

          sleep_quality = entry["params"][0]
          teams_sleep[team][sleep_quality] += 1

          if sleep_quality == "tosi hyvin":
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
        teams_activity[kind][team] += 1

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

  def weighted_sum(points_tuple, weights):
    size = team_sizes[points_tuple[0]]
    return sum([weights[name] * count for (name, count) in points_tuple[1].items()])

  most_dokattu = max(teams_alcohol.items(),
      key = lambda x: weighted_sum(x, alcohol_weights)
      #lambda x: x[1]
      )

  def least_dokattu_key(x):
    name = x[0]
    #divisor = 1.0 * (teams_activity["good"][name] + teams_activity["bad"][name])
    divisor = sum(teams_alcohol[name].values())
    divisor *= team_sizes[name]
    return weighted_sum(x, alcohol_weights) / divisor

  least_dokattu = min(teams_alcohol.items(),
      #key = lambda x: weighted_sum(x, alcohol_weights) / (teams_activity["bad"][x[0]] + teams_activity["good"][x[0]])
      key = least_dokattu_key,
      #key = lambda x: x[1]["ei ollenkaan!"] / team_sizes[x[0]]
      #key = lambda x: x[1]["ei ollenkaan!"] / sum(x[1].values()) #teams_activity["good"][x[0]]
      )

  tissuttelu = max(teams_alcohol.items(), key = lambda x: x[1]["no blast"] / team_sizes[x[0]])

  most_sporty = max(teams_sports.items(), key = lambda x: x[1] / team_sizes[x[0]])
  least_sporty = min(teams_sports.items(), key = lambda x: x[1] / team_sizes[x[0]])

  best_food = max(teams_food.items(),
      #key = lambda x: sum([food_weights[y[0]] * y[1] for y in x[1].items()]) / team_sizes[x[0]]
      key = lambda x: weighted_sum(x, food_weights)
      )

  worst_food = min(teams_food.items(),
      #key = lambda x: sum([food_weights[y[0]] * y[1] for y in x[1].items()]) / team_sizes[x[0]]
      key = lambda x: weighted_sum(x, food_weights)
      )

  best_sleep = max(teams_sleep.items(),
      key = lambda x: weighted_sum(x, sleep_weights)
      )

  worst_sleep = min(teams_sleep.items(),
      key = lambda x: weighted_sum(x, sleep_weights)
      )

  most_stress = max(teams_stress.items(),
      key = lambda x: weighted_sum(x, stress_weights)
      )

  least_stress = min(teams_stress.items(),
      key = lambda x: weighted_sum(x, stress_weights)
      )

  most_good_day = max(daily_points["good"].items(), key = lambda x: x[1] / daily_counts["good"][x[0]])
  most_bad_day =  max(daily_points["bad"] .items(), key = lambda x: x[1] / daily_counts["bad"][x[0]])
  most_dokattu_day = max(daily_alcohol.items(), key = lambda x: x[1] / daily_counts["bad"][x[0]])

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
  #leg.set_draggable(True)
  leg.draggable()

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
  #leg.set_draggable(True)
  leg.draggable()

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
  #leg.set_draggable(True)
  leg.draggable()

  #}}}

def plot_average_daily_points():

  #{{{
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

  #}}}

def plot_average_daily_alcohol():
  fig = plt.figure()
  ax2 = fig.gca()
  ax = ax2.twinx()

  t = np.array(list(daily_alcohol.keys()  ))
  a = np.array(list(daily_alcohol.values()))
  c = np.array([daily_counts["good"][t1] for t1 in t])

  t_sort_i = np.argsort(t)
  t = t[t_sort_i] + datetime.timedelta(days = -1)
  a = a[t_sort_i]
  c = c[t_sort_i]

  t = t.astype(np.datetime64) + np.timedelta64(1, "D")

  t_bo = np.array(list(daily_blackouts.keys()), dtype = np.datetime64)
  bo = np.array(list(daily_blackouts.values()))

  lines_to_label = []
  labels = []

  l = ax.plot(t, a * 1.0 / c, marker = "s", zorder = 20)
  lines_to_label.append(l[0])
  labels.append("Alkoholipisteet")

  red = "#d62728"
  for i, t1 in enumerate(t_bo):
    l = ax2.plot([t1, t1], [0, bo[i]],
        color = red, linewidth = 10,
        label = "bläkärien lkm" if i == 0 else None,
        )

    if i == 0:
      lines_to_label.append(l[0])
      labels.append("Bläkärit")

  for i, friday in enumerate(t[np.is_busday(t, weekmask = "Fri")] + np.timedelta64(1, "D")):
    l = ax.plot( [friday, friday], [0, 2],
        color = red, alpha = 0.5, linestyle = "--",
        #label = "Perjantai" if i == 0 else None
        zorder = 1
        )
    if i == 0:
      lines_to_label.append(l[0])
      labels.append("Perjantai")

  ax.set_ylabel("Alkoholipisteet / Osallistuja")
  ax2.set_ylabel("Bläkärien lkm")

  ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m."))
  ax.xaxis.set_major_locator(mdates.DayLocator(interval = 3))
  ax.yaxis.tick_left()
  ax.yaxis.set_label_position("left")
  ax2.yaxis.tick_right()
  ax2.yaxis.set_label_position("right")

  leg = ax2.legend(lines_to_label[::-1], labels[::-1])
  leg.draggable()

#plot_stress_multihist()
#plot_alcohol_multihist()
#plot_team_cumulative_points()
#plot_average_daily_points()
plot_average_daily_alcohol()

def print_team_points_dict(s, tup):
  print(s.format(tup[0], dict(tup[1])))

# mielen kiintoisia faktoja
print("total sports hours: {:.2f} (variance {:.2f})".format(total_sports_hours, np.var(sports_hours)))
print("total blackouts: {}".format(sum([x["bläkäri"] for x in alcohol.values()])))
print("full blast count: {}".format(sum([x["full blast"] for x in alcohol.values()])))
print("no blast count: {}".format(sum([x["no blast"] for x in alcohol.values()])))
print("ei ollenkaan count: {}".format(sum([x["ei ollenkaan!"] for x in alcohol.values()])))
print("no. of well slept nights: {}".format(n_well_slept_nights))
print_team_points_dict("\ndokatuin joukkue:\n{}\n{}", most_dokattu)
print_team_points_dict("\nvähiten dokattu joukkue:\n{}\n{}", least_dokattu)
print("{} (alkoholipisteet / (alkoholimerkinnät * joukkueen koko))".format(least_dokattu_key(least_dokattu)))
print_team_points_dict("\npahimmat tissuttelijat (eniten no blast merkintöjä):\n{}\n{}", tissuttelu)
print("\neniten urheilupisteitä: {} - {:.2f}".format(* most_sporty))
print("\nvähiten urheilupisteitä: {} - {:.2f}".format(* least_sporty))
print_team_points_dict("\nparhaiten nukkuneet:\n{}\n{}", best_sleep)
print_team_points_dict("\nhuonoiten nukkuneet:\n{}\n{}", worst_sleep)
print_team_points_dict("\nparhaiten syöneet:\n{}\n{}", best_food)
print_team_points_dict("\nhuonoiten syöneet:\n{}\n{}", worst_food)
print_team_points_dict("\nstressaantunein joukkue:\n{}\n{}", most_stress)
print_team_points_dict("\nvähiten stresssaantunut joukkue:\n{}\n{}", least_stress)
print("\nHyvinvoivin päivä: {} ({:.2f} pistettä / hlö)".format(most_good_day[0], most_good_day[1] / daily_counts["good"][most_good_day[0]]))
print("\nPahoinvoivin päivä: {} ({:.2f} pistettä / hlö)".format(most_bad_day[0], most_bad_day[1] / daily_counts["bad"][most_bad_day[0]]))
print("\ndokatuin päivä: {} {:.2f} alkoholipistettä / kaikki pahoinvointimerkinnät".format(most_dokattu_day[0], most_dokattu_day[1] / daily_counts["bad"][most_dokattu_day[0]]))

def print_rankings(kind):
  for (i, (name, score)) in enumerate(rankings[kind].items()):
    print("{:2}. {} - {:.2f}".format(i + 1, name, score))

if False: # print  final rankings
  print("\n"); print("RANKINGS:\n");
  print("Hyvinvointi:\n");  print_rankings("good");    print("\n")
  print("Pahoinvointi:\n"); print_rankings("bad");     print("\n")
  print("sum abs:\n");      print_rankings("sum abs"); print("\n")
  print("diff:\n");         print_rankings("diff");

plt.show(block = not ipython)

# vim: set fdm=marker :
