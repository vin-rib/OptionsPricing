import numpy as np

from derivatives import ValuationClass
from derivatives import plot_option_stats


def binary_classifier(value, strike):
    if value >= strike:
        return 1.0
    else:
        return 0.0


class ValuationEuropeanMonteCarlo(ValuationClass):
    """ Class to value European options with arbitrary payoff
    by single-factor Monte Carlo simulation ( Just only for PUT and CALLS )."""

    def generate_payoff(self, fixed_seed=False):
        strike = self.strike
        option_type = self.option_type
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
        # average value over whole path
        mean_value = np.mean(paths[:time_index], axis=1)
        # maximum value over whole path
        max_value = np.amax(paths[:time_index], axis=1)[-1]
        # minimum value over whole path
        min_value = np.amin(paths[:time_index], axis=1)[-1]
        if option_type == 'European':
            try:
                payoff = eval(self.payoff_func)
                return payoff
            except Exception as error:
                print(f"Maturity date not in time grid of underlying. {error}")
        elif option_type == 'Binary':
            try:
                payoff = np.array([binary_classifier(value, strike) for value in maturity_value])
                return payoff
            except Exception as error:
                print(f"Maturity date not in time grid of underlying. {error}")
        else:
            return None

    def present_value(self, accuracy=6, fixed_seed=False, full=False):
        cash_flow = self.generate_payoff(fixed_seed=fixed_seed)
        discount_factor = self.discount_curve.get_discount_factors(
            (self.pricing_date, self.maturity))[0, 1]
        result = discount_factor * np.sum(cash_flow) / len(cash_flow)
        if full:
            return round(result, accuracy), discount_factor * cash_flow
        else:
            return round(result, accuracy)

    def generate_plot(self, initial_value, final_value, increase):
        s_list = np.arange(initial_value, final_value, increase)
        p_list = []
        d_list = []
        v_list = []
        for s in s_list:
            self.update(initial_value=s)
            p_list.append(self.present_value(fixed_seed=True))
            d_list.append(self.delta())
            v_list.append(self.vega())
        plot_option_stats(s_list, p_list, d_list, v_list)
