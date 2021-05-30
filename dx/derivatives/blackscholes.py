import numpy as np
import scipy
import matplotlib.pyplot as plt
import pandas as pd


class BlackScholes:
    """
    Classe usada parar armazenar dados de uma opção europeia para serem calculados métricas utilizando o modelo de Black-Scholes
    ...
    Propiedades
    ---------
    d1 : flt

    d2 : flt

    Probabilidade da opção expirar in the money
    Methods
    -------
    get_user_input()
        Requisita entradas do usuário pra construir um objeto com os parametros dados

    """

    def __init__(self, asset_price, strike, maturity_time, risk_free_factor, sigma, option_type, time=0):
        self.asset_price = asset_price
        self.strike = strike
        self.maturity_time = maturity_time
        self.risk_free_factor = risk_free_factor
        self.sigma = sigma
        self.opt = option_type
        self.time = time

    @property
    def d1(self):
        return (np.log(self.asset_price / self.strike) + (self.risk_free_factor + 0.5 * self.sigma ** 2) *
                (self.maturity_time - self.time)) / (self.sigma * np.sqrt(self.maturity_time - self.time))

    @property
    def d2(self):
        return self.d1 - self.sigma * np.sqrt(self.maturity_time - self.time)

    def update(self, initial_time, stock_price, strike=None):
        if initial_time is not None:
            self.time = initial_time
        if stock_price is not None:
            self.asset_price = stock_price
        if strike is not None:
            self.strike = strike

    @property
    def price(self):
        """
        Retorna o preço da opção, calculado a partir da solução da equação e Black-Scholes
        """
        if self.opt == "eurocall":
            return self.asset_price * scipy.stats.norm.cdf(self.d1, 0.0, 1.0) - self.strike * np.exp(
                -self.risk_free_factor * self.maturity_time) * scipy.stats.norm.cdf(self.d2, 0.0, 1.0)
        elif self.opt == "europut":
            return (self.strike * np.exp(-self.risk_free_factor * (self.maturity_time - self.time)) *
                    scipy.stats.norm.cdf(-self.d2, 0.0, 1.0) - self.asset_price * scipy.stats.norm.cdf(
                        -self.d1, 0.0, 1.0))
        else:
            print("Tipo de opção inválido, defina o tipo igual 1 para uma call e igual a 0 para um put")

    @property
    def delta(self):
        """
        Retorna o delta da opção, a derivada do preço da opção em respeito ao preço da ação
        """
        if self.opt == "eurocall":
            return scipy.stats.norm.cdf(self.d1, 0.0, 1.0)
        elif self.opt == "europut":
            return scipy.stats.norm.cdf(self.d1, 0.0, 1.0) - 1
        else:
            print("Tipo de opção inválido, defina o tipo igual 1 para uma call e igual a 0 para um put")

    @property
    def gamma(self):
        """
        Retorna o gamma da opção, a segunda derivada do preço da opção em respeito ao preço da ação
        """
        return (scipy.stats.norm.pdf(self.d1) * np.exp(self.maturity_time - self.time)) / (
                self.asset_price * self.sigma * np.sqrt(self.maturity_time - self.time))

    @property
    def vega(self):
        """
        Retorna o vega da opção, a derivada do preço da opção em respeito a volatilidade
        """
        return (scipy.stats.norm.pdf(self.d1) * np.exp(self.maturity_time - self.time)) * \
               (self.asset_price * np.sqrt(self.maturity_time - self.time))
    
    @staticmethod
    def imp_vol(self, sigma0, actual_price, iter=100):
        # Todo: remove from here
        """
        Obtém a raiz da função BS_price(sigma) - actual_price utilizando o método de newton, onde a a derivada em relação a volatilidade é o vega da opção
        """
        option = BlackScholes(self.asset_price, self.strike, self.maturity_time, self.risk_free_factor, sigma0,
                              self.tipo, self.time)
        for i in range(iter):
            option.sigma = option.sigma - (option.price() - actual_price) / option.vega()
        return option.sigma

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

    def delta_hedging(self, number_steps, n_options=1, seed=2, *args):
        """
        Estratégia de delta hedging para uma venda de call option
        :param number_steps:
        :param n_options:
        :param seed:
        :param args:
        :return:
        """
        if not args:
            path, ts = self.gmb_path(number_steps=number_steps, seed=seed)
        else:
            path, ts = args
        stocks = np.zeros(len(path))
        deltas = np.zeros(len(path))
        delta_position = np.zeros(len(path))
        cash = np.zeros(len(path))
        cash[0] = self.price
        opt_price = np.zeros(len(path))
        ds_list = []

        for i in range(len(path)):
            opt_price = self.price
            deltas[i] = round(self.delta, 3)
            delta_position[i] = deltas[i] * n_options
            stocks[i] = - delta_position[i] / path[i]
            if i != 0:
                ds = round(stocks[i] - stocks[i - 1], 4)
                cash[i] += ds * path[i]
                ds_list.append(ds)
                if ds > 0:
                    print("actual delta:{}".format(deltas[i]),
                          "Buy {} shares at {}".format(ds, path[i]))
                if ds < 0:
                    print("actual delta:{}".format(deltas[i]),
                          "Sell {} shares at {}".format(ds, path[i]))
            elif i == 0:
                ds = round(stocks[i], 4)
                cash[i] += ds * path[i]
                ds_list.append(ds)
                if ds > 0:
                    print("actual delta:{}".format(deltas[i]),
                          "Buy {} shares at {}".format(ds, path[i]))
                if ds < 0:
                    print("actual delta:{}".format(deltas[i]),
                          "Sell {} shares at {}".format(ds, path[i]))
            self.update(initial_time=ts[i], stock_price=path[i])

        data = {"delta": deltas,
                "shares purchased": ds_list,
                "total_shares": stocks,
                "stock_price": path,
                "delta_position": delta_position}
        df = pd.DataFrame(data=data)
        results = np.array(ds_list) @ path
        return results, df

        # todo check this code
        # if (stocks[-1]<n_options) and (path[-1]>=self.strike):
        #  results = cash[-1] + (n_options - stocks[-1])*(self.strike - path[-1])
        # if (stocks[-1]>=n_options) and (path[-1]>=self.strike):
        #  results = cash[-1] + (stocks[-1]-n_options)*path[-1]
        # if path[-1]<self.strike:
        #  results = cash[-1] + stocks[-1]*path[-1]
        # else:
        # results = cash[-1]
        # return ts,stocks,cash,results

    def stop_loss(self, pct=0, number_steps=100, seed=2, plot=False, *args):
        """
        estratégia de comprar quando passar do strike e vender quando estiver abaixo
        :param pct:
        :param number_steps:
        :param seed:
        :param plot:
        :param args:
        :return:
        """
        if not args:
            path, ts = self.gmb_path(number_steps=number_steps, seed=seed)
        else:
            path, ts = args
        n = len(path)
        cash = np.zeros(n)
        shares = 0
        buy_list = []
        sell_list = []
        results = None
        for i in range(len(path)):
            if (path[i] > (1 + pct / 100) * self.strike) and (shares == 0):
                shares += 1
                cash[i] -= path[i]
                buy_list.append([ts[i], path[i]])
            if (path[i] < (1 - pct / 100) * self.strike) and (shares == 1):
                shares -= 1
                cash[i] += path[i]
                sell_list.append([ts[i], path[i]])
            else:
                pass
        if (shares == 0) and (path[-1] >= self.strike):
            # se o preço no tempo final for maior que o strike a opção será executada e o
            # vendedor da call deverá comprar o ativo no preço deste no final do trajeto
            results = cash[-1] + (-path[-1] + self.strike)
            buy_list.append([ts[-1], path[-1]])
        if (shares == 1) and (path[-1] >= self.strike):
            # se o preço no tempo final for maior que o strike a opção
            # será executada e o vendedor da call não precisará comprar o ativo se já possui
            results = cash[-1] - self.strike
        if path[-1] < self.strike:  # se o preço estiver abaixo do strike a opção não será executada
            results = cash[-1]
            # todo MAIS UM IF
        buy_list = np.array(buy_list)
        sell_list = np.array(sell_list)
        if plot:
            plt.figure(figsize=(15, 6))
            plt.plot(ts, path)
            plt.plot(buy_list[:, 0], buy_list[:, 1], linestyle="None", marker="o", color="green", label="Buy")
            plt.plot(sell_list[:, 0], sell_list[:, 1], linestyle="None", marker="o", color="red", label="Sell")
            plt.plot(ts, [self.strike] * len(ts), linestyle="dashed", label="Strike")
            if pct != 0:
                plt.plot(ts, [self.strike * (1 + pct / 100)] * len(ts), linestyle="dotted", label="Safety margin up")
                plt.plot(ts, [self.strike * (1 - pct / 100)] * len(ts), linestyle="dotted", label="Safety margin down")
            plt.legend()

            plt.show()
        return results
