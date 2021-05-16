# using usr/bin/python3
import numpy as np
from derivatives import sn_random_numbers
from derivatives import SimulationClass
import matplotlib.pyplot as plt


class GeometricBrownianMotion(SimulationClass):
    """ Class to generate simulated paths based on
    the Black-Scholes-Merton geometric Brownian motion model."""

    def __init__(self, name, mar_env):
        super(GeometricBrownianMotion, self).__init__(name, mar_env)

    def update(self, initial_value=None, volatility=None, final_date=None):
        if initial_value is not None:
            self.initial_value = initial_value
        if volatility is not None:
            self.volatility = volatility
        if final_date is not None:
            self.final_date = final_date
        self.instrument_values = None

    def generate_paths(self, fixed_seed=False, day_count=365.):
        if self.time_grid is None:
            # method from generic simulation class
            self.generate_time_grid()
        # number of dates for time grid    
        M = len(self.time_grid)
        # number of paths
        path_number = self.paths
        # array initialization for path simulation
        paths = np.zeros((M, path_number))
        # initialize first date with initial_value
        paths[0] = self.initial_value
        # generate random numbers
        random_dist = sn_random_numbers((1, M, path_number), fixed_seed=fixed_seed)
        short_rate = self.discount_curve.short_rate
        # get short rate for drift of process
        # TODO : To be vectorized
        for t in range(1, len(self.time_grid)):
            # random number set
            random_dist_step = random_dist[t]
            dt = (self.time_grid[t] - self.time_grid[t - 1]).days / day_count
            # difference between two dates as year fraction
            paths[t] = paths[t - 1] * np.exp((short_rate - 0.5
                                              * self.volatility ** 2) * dt
                                             + self.volatility * np.sqrt(dt) * random_dist_step)
            # generate simulated values for the respective date
        self.instrument_values = paths

    def plot(self, path_model):
        plt.figure(figsize=(10, 6))
        model1 = plt.plot(self.time_grid, path_model[0][:, :30], label='Low Volatility', color='r',
                          linestyle='--', linewidth=1)
        model2 = plt.plot(self.time_grid, path_model[1][:, :30], label='High Volatility', color='b',
                          linestyle='--', linewidth=1)

        # # Create a legend for the first line.
        legends = plt.legend(handles=[model1[0], model2[0]], loc='upper right')

        # # Add the legend manually to the current Axes.
        plt.gca().add_artist(legends)

        # # Create another legend for the second line.
        plt.grid(b=True, which='both', color='#999999', linestyle='-', alpha=0.9)

        plt.show()

