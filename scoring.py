"""
This module contains functions for calculating scores for different types of activities.
Each function takes a list as a parameter and computes the score based on that.
"""

#TODO: is this the best way to do this?

def liikunta_score(params):
  assert type(params) == list
  # params = [intensity, duration]
  print("liikunta_score(): {}".format(params))
  score = params[0] * params[1] #TODO: replace this with something that is not linear in duration

  return score
