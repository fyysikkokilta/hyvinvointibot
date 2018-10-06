"""
This module contains functions for calculating scores for different types of activities.
Each function takes a list as a parameter and computes the score based on that.
The score is returned wrapped into a score object, which has a type "good" 
(hyvinvointi) or "bad" (pahoinvoint) and a numeric value.
"""

GOOD_KEY = "good"
BAD_KEY = "bad"

class ScoreObject():

  def __init__(self, value, _type, params):
    """
    params: the parameters that were used to calculate value
    """
    assert _type in [GOOD_KEY, BAD_KEY]
    value = float(value)
    self.type = _type
    self.value = value
    self.parameters = params

  def __repr__(self):
    return "{}({})".format(self.__class__, self.__dict__)


def liikunta_score(params):
  # params = ['Liikunta', intensity, duration]
  assert type(params) == list
  print("liikunta_score(): {}".format(params))
  score = params[1] * params[2] #TODO: replace this with something that is not linear in duration

  return ScoreObject(score, "good", params)

def alkoholi_score(params):
  # params: should just be a float
  return ScoreObject(abs(params), "bad", params)


########################
# VALIDATION FUNCTIONS #
########################

def validate_number(number_str, a, b):
  """
  return float(number_str) if number_str is a number and is in the range [a, b],
  otherwise return None
  """
  try:
    n = float(number_str)
    if a <= n <= b:
      return n
    else: return None

  except ValueError:
    return None

def liikunta_validate_intensity(intensity_str):
  return validate_number(intensity_str, 0, 5)

def liikunta_validate_duration(duration_str):
  return validate_number(duration_str, 0, 12)
