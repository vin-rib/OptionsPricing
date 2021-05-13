# using usr/bin/python3
from derivatives_module import get_year_deltas
import numpy as np


class ConstantShortRate:
    """ Class to generate constant short rate from a datetime list."""
    def __init__(self, name, short_rate):
        self.name = name
        self.short_rate = short_rate
        if short_rate < 0:
            raise ValueError('Short rate negative.')

    def get_discount_factors(self, date_list, datetime_objects=True):
        if datetime_objects is True:
            datetime_list = get_year_deltas(date_list)
        else:
            datetime_list = np.array(date_list)
        disc_factor_list = np.exp(self.short_rate * np.sort(-datetime_list))
        return np.array((date_list, disc_factor_list)).T
