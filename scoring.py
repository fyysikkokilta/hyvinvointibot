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

# return True if number_str is a number and is in the range [a, b]
def validate_number(number_str, a, b):
  try:
    n = float(number_str)
    return a <= n <= b

  except ValueError:
    return False

def liikunta_validate_intensity(intensity_str):
  return validate_number(intensity_str, 0, 5)

def liikunta_validate_duration(duration_str):
  return validate_number(duration_str, 0, 12)
