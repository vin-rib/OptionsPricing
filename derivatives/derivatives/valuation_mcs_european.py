import numpy as np

from derivatives_module import ValuationClass


class ValuationEuropeanMonteCarlo(ValuationClass):
    """ Class to value European options with arbitrary payoff
    by single-factor Monte Carlo simulation."""

    def generate_payoff(self, fixed_seed=False):
        strike = self.strike
        time_index = None
        paths = self.underlying.get_instrument_values(fixed_seed=fixed_seed)
        time_grid = self.underlying.time_grid
        try:
            time_index = np.where(time_grid == self.maturity)[0]
            time_index = int(time_index)
        except Exception as error:
            print(f"Maturity date not in time grid of underlying. {error}")
        # used on the payoff method
        maturity_value = paths[time_index]
        try:
            payoff = eval(self.payoff_func)
            return payoff
        except Exception as error:
            print(f"Maturity date not in time grid of underlying. {error}")

    def present_value(self, accuracy=6, fixed_seed=False, full=False):
        cash_flow = self.generate_payoff(fixed_seed=fixed_seed)
        discount_factor = self.discount_curve.get_discount_factors(
            (self.pricing_date, self.maturity))[0, 1]
        result = discount_factor * np.sum(cash_flow) / len(cash_flow)
        if full:
            return round(result, accuracy), discount_factor * cash_flow
        else:
            return round(result, accuracy)
