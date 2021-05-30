import matplotlib.pyplot as plt
import numpy as np


class Pricing:
    def __init__(self, asset_price, strike, maturity_time, risk_free_factor, sigma, time=0, function_payoff=None):
        self.ts = None
        self.opt = None
        self.path = None
        self.payoffs = None
        self.time = time
        self.sigma = sigma
        self.strike = strike
        self.asset_price = asset_price
        self.maturity_time = maturity_time
        self.function_payoff = function_payoff
        self.risk_free_factor = risk_free_factor

    def update(self, initial_time, stock_price):
        if initial_time is not None:
            self.time = initial_time
        if stock_price is not None:
            self.asset_price = stock_price

    def __getitem__(self, key):
        if key == 1 or key == 'r':
            return self.__r
        if key == 2 or key == 'vol':
            return self.__sigma
        if key == 3 or key == 'T':
            return self.__T
        return None

    def __setitem__(self, key, value):
        if key == 1 or key == 'r':
            try:
                self.__r = value
            except TypeError:
                print('Erro de troca')
            self.__r = value
        if key == 2 or key == 'vol':
            try:
                self.__sigma = value
            except TypeError:
                print('Erro de troca')
        if key == 3 or key == 'T':
            try:
                self.__T = value
            except TypeError:
                print('Erro de troca')

    def gmb_path(self, number_steps=100, seed=2, plot=False):
        np.random.seed(seed)
        n_steps = number_steps
        ts, dt = np.linspace(0, self.maturity_time, n_steps, retstep=True)
        asset_price_vector = np.zeros(n_steps)
        asset_price_vector[0] = self.asset_price
        normal_vector = np.random.normal(0, np.sqrt(dt), n_steps)
        cumulative_step_vector = np.cumsum(normal_vector)
        for i in range(1, n_steps):
            asset_price_vector[i] = self.asset_price * np.exp((self.risk_free_factor - 0.5 * self.sigma * self.sigma) *
                                                              ts[i - 1] + self.sigma * cumulative_step_vector[i])
        if plot:
            plt.plot(ts, cumulative_step_vector)
            plt.show()
        return asset_price_vector, ts

    def generate_paths(self, number_steps=100, number_paths=10):
        seed_list = np.random.random(number_paths)
        self.path = np.empty((number_paths, number_steps))
        self.ts = np.linspace(0, self.maturity_time, number_steps)
        for i in range(number_paths):
            self.path[i], __ = self.gmb_path(number_steps, seed=seed_list[i])

    def opt_sim(self, opt='euro_call', number_steps=100, number_paths=10):
        self.opt = opt
        self.generate_paths(number_steps, number_paths)
        self.payoffs = np.empty((number_paths, 1))
        for i in range(number_paths):
            # European
            if self.opt == 'euro_call':
                self.payoffs[i] = np.max(0, self.path[i][-1] - self.strike)
            if self.opt == 'euro_put':
                self.payoffs[i] = np.max(0, -self.path[i][-1] + self.strike)
            # Binary
            if self.opt == 'binary_call':
                if self.path[i][-1] > self.strike:
                    self.payoffs[i] = 1
                else:
                    self.payoffs[i] = 0
            if self.opt == 'binary_put':
                if self.path[i][-1] < self.strike:
                    self.payoffs[i] = 1
                else:
                    self.payoffs[i] = 0
            # Asian
            if self.opt == 'asian_call':
                self.payoffs[i] = np.max(0, np.mean(self.path[i]) - self.strike)
            if self.opt == 'asian_put':
                self.payoffs[i] = np.max(0, -np.mean(self.path[i]) + self.strike)
            # Custom
            if self.function_payoff is not None:
                self.payoffs[i] = eval(self.function_payoff)
        return np.exp(-self.risk_free_factor * self.maturity_time) * np.sum(self.payoffs, axis=0) / number_paths