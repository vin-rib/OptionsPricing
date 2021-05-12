# using usr/bin/python3
import numpy as np


def get_year_deltas(date_list, day_count=365.):
    """
    Return vector of floats with day deltas in years
    :param date_list: (list) datetime objects
    :param day_count: (float) number of days in year
    :return: (np.array) array with fraction of year
    """
    start = date_list[0]
    delta_list = [(date - start).days / day_count
                  for date in date_list]
    return np.array(delta_list)
