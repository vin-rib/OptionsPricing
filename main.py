import numpy as np
import datetime as dt
from derivatives import MarketEnvironment
from derivatives import ConstantShortRate
from derivatives import GeometricBrownianMotion
from derivatives import ValuationEuropeanMonteCarlo
from derivatives import plot_option_stats

me_gbm = MarketEnvironment('me_gbm', dt.datetime(2020, 1, 1))
me_gbm.add_constant('initial_value', 36.)
me_gbm.add_constant('volatility', 0.2)
me_gbm.add_constant('final_date', dt.datetime(2020, 12, 31))
me_gbm.add_constant('currency', 'EUR')
me_gbm.add_constant('frequency', 'M')
me_gbm.add_constant('paths', 1000)

csr = ConstantShortRate('csr', 0.06)
me_gbm.add_curve('discount_curve', csr)
gbm = GeometricBrownianMotion('gbm', me_gbm)

me_call = MarketEnvironment('me_call', me_gbm.pricing_date)
me_call.add_constant('strike', 20.)
me_call.add_constant('maturity', dt.datetime(2021, 12, 31))
me_call.add_constant('currency', 'EUR')


payoff_func = "np.maximum(maturity_value - strike, 0)"
eur_call = ValuationEuropeanMonteCarlo('eur_call', underlying=gbm,
                                       mar_env=me_call, payoff_func=payoff_func, option_type='KnockinBarrier')
print(eur_call.present_value(barrier=10))
print(eur_call.delta())
print(eur_call.vega())

s_list = np.arange(34., 46.1, 2.)
p_list = []
d_list = []
v_list = []

for s in s_list:
    eur_call.update(initial_value=s)
    p_list.append(eur_call.present_value(fixed_seed=True))
    d_list.append(eur_call.delta())
    v_list.append(eur_call.vega())

plot_option_stats(s_list, p_list, d_list, v_list)
