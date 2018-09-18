import pandas as pd
import math
from math import log, sqrt, pi, exp
from os.path import dirname, join
import datetime

DATA_DIR = '/home/francois/Python/Dashboard/'
PRICE_DIR = '/home/francois/2trader/'

def norm_pdf(x):
    """
    Standard normal probability density function
    """
    return (1.0/((2*pi)**0.5))*exp(-0.5*x*x)

def norm_cdf(x):
    """
    An approximation to the cumulative distribution
    function for the standard normal distribution:
    N(x) = \frac{1}{sqrt(2*\pi)} \int^x_{-\infty} e^{-\frac{1}{2}s^2} ds
    """
    k = 1.0/(1.0+0.2316419*x)
    k_sum = k * (0.319381530 + k * (-0.356563782 + \
        k * (1.781477937 + k * (-1.821255978 + 1.330274429 * k))))

    if x >= 0.0:
        return (1.0 - (1.0 / ((2 * pi)**0.5)) * exp(-0.5 * x * x) * k_sum)
    else:
        return 1.0 - norm_cdf(-x)

def d_j(j, S, K, r, v, T):
    """
    d_j = \frac{log(\frac{S}{K})+(r+(-1)^{j-1} \frac{1}{2}v^2)T}{v sqrt(T)}
    """
    return (log(S/K) + (r + ((-1)**(j-1))*0.5*v*v)*T)/(v*(T**0.5))

def vanilla_call_price(S, K, r, v, T):
    """
    Price of a European call option struck at K, with
    spot S, constant rate r, constant vol v (over the
    life of the option) and time to maturity T
    """
    return S * norm_cdf(d_j(1, S, K, r, v, T)) - \
        K*exp(-r*T) * norm_cdf(d_j(2, S, K, r, v, T))

def vanilla_put_price(S, K, r, v, T):
    """
    Price of a European put option struck at K, with
    spot S, constant rate r, constant vol v (over the
    life of the option) and time to maturity T
    """
    return -S * norm_cdf(-d_j(1, S, K, r, v, T)) + \
        K*exp(-r*T) * norm_cdf(-d_j(2, S, K, r, v, T))

def option_price(strike, spot, ytm, rates, callput, volatility):
    
    if callput.lower() == "p":
        result= vanilla_put_price(spot, strike, rates, volatility, ytm)
    elif callput.lower() == "c":   
        result = vanilla_call_price(spot, strike, rates, volatility, ytm)

    return result

def implied_vol(price, strike, fwd, ytm, rates, callput, nbloops, precision, minvol, maxvol):
    
    tmpvol1 = maxvol
    tmpvol2 = minvol
    df = exp(- rates * ytm)

    if callput.lower() == "p":
        cp = -1
    elif callput.lower() == "c":
        cp = 1

    i = 0
    while abs(tmpvol1 - tmpvol2) > precision and i < nbloops:
        tmpvol2 = tmpvol1
        d1 = log(fwd / strike) / (tmpvol2 * sqrt(ytm)) + (tmpvol2 * sqrt(ytm)) * 0.5
        price1 = df * cp * (fwd * norm_cdf(cp * d1) - strike * norm_cdf(cp * (d1 - tmpvol2 * sqrt(ytm))))
        vega1 = df * fwd * sqrt(ytm) * norm_pdf(d1)
        tmpvol1 = tmpvol2 + (price - price1) / vega1
        i = i + 1

    return (i, tmpvol1)

# GET KOSPI FROM FAIRDUMP FILE

fname = join(PRICE_DIR, 'kospi_closing_prices.csv')
prices = pd.read_csv(fname)
header = prices.columns

# IMPLICITATION PARAMETERS
rates = 0.015
nbloops = 200
precision = 0.01
minvol = 0.05
maxvol = 1.50

output = []
for line in range(len(prices)):
    
    data = prices.iloc[line]
    output_line = []

    year = int(data[0][:4])
    month = int(data[0][5:7])
    day = int(data[0][8:10])
    
    date = datetime.date(year, month, day)
    date = datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%B %d, %Y')
    
    mat = data[1]
    ytm = float(data[2])
    fwd = float(data[3])
    strol = float(data[4])

    # append output
    output_line.append(date)
    output_line.append(mat)
    output_line.append(ytm)

    nb_strike= int((len(data) - 5)  / 2)

    for i in range(nb_strike):
        
        col = 4 + (2*i + 1)
        strike = float(data[col])
        callput = header[col][:-(len('strike')+1)][-1:]
        price = float(data[col+1])
        
        try:
            impli = implied_vol(price/100, strike/100, fwd/100, ytm, rates, callput, nbloops, precision, minvol, maxvol)
            vol = 100 * impli[1]
        except:
            vol = 0
        
        output_line.append(vol)

    output.append(output_line)

raw_data = pd.DataFrame(output)

# REVERSE THE DATA FRAME
implied = raw_data[::-1]

# CREATE THE BASE FILE
implied.to_csv(DATA_DIR + 'KOSPI 200 DATABASE.csv', header = None, index = None)

# GENERATE VARIOUS CSV FILE FOR THE DASHBOARD

# GENERATE THE CURVE COMPARISON

implied_vol = implied.copy()
implied_vol['index'] = implied_vol[implied_vol.columns[0]] + ': ' + implied_vol[implied_vol.columns[1]]
implied_vol[implied_vol.columns[0]] = implied_vol['index']
del implied_vol['index']
del implied_vol[implied_vol.columns[1]]
del implied_vol[implied_vol.columns[1]]

implied_vol.to_csv(DATA_DIR + 'KOSPI 200 Implied Volatility.csv', header = None, index = None)

# GENERATE THE VOLATILITY HISTORIC PER STRIKE

"""
GENERATE THE VOLATILITY HISTORIC PER STRIKE
TO GENERATE THE "VOLATILITY", LET'S CREATE SOME SYNTHETIC 15D VOLATILITY
    1. IF TWO VOLATILITIES AVAILABLE : BARYCENTER THE TWO BY YTM
    2. IF ONE VOLATILITY AVAILABLE   : NOTHING TO DO

"""

strike_vol = implied.copy()

# RETRIEVE THE STRIKE LIST FROM THE HEADER

strike_list = []
nb_strike= int((len(data) - 5)  / 2)

for word in header:
    if word[-5:] == 'price':
        strike_list.append(int(word[:-8]))

i = 0
for strike in strike_list:

    output_strike = []
    date_list = []

    for line in range(len(strike_vol)):

        if line < len(strike_vol) -1:
            
            output = []
            new_value = False

            data_curr = strike_vol.iloc[line]
            data_next = strike_vol.iloc[line + 1]

            date = data_curr[0]

            if data_curr[0] == data_next[0]:
                # data on two expiries
                vol1 = data_curr[3 + i]
                ytm1 = data_curr[2]

                vol2 = data_next[3 + i]
                ytm2 = data_next[2]
            
                vol_blend =(vol1 * ytm1 + vol2 * ytm2) / (ytm1 + ytm2)

                # add the expiry to the treated list
                new_value = True
                date_list.append(data_curr[0])
                output.append(date)
                output.append(vol_blend)
            else:
                
                if data_curr[0] not in date_list:
                    # data on one expiriy
                    vol1 = data_curr[3 + i]
                    ytm1 = data_curr[2]

                    vol_blend = vol1

                    new_value = True
                    output.append(date)
                    output.append(vol_blend)

            if new_value == True:
                output_strike.append(output)
    i = i + 1

    df = pd.DataFrame(output_strike)
    df.to_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(strike) + '.csv', header = None, index = None)

"""

GENERATE THE SKEW & CONVEXITY SPREAD
TO GENERATE THE "VOLATILITY", LET'S CREATE SOME SYNTHETIC 15D VOLATILITY
    1. IF TWO VOLATILITIES AVAILABLE : BARYCENTER THE TWO BY YTM
    2. IF ONE VOLATILITY AVAILABLE   : NOTHING TO DO

"""

# SKEW SPREADS

spread_strike = [5, 10, 15, 20, 30, 40]

for spread in spread_strike:
    
    put_strike = 100 - spread
    call_strike = 100 + spread

    put_data  = pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(put_strike) + '.csv', header = None)
    call_data =  pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(call_strike) + '.csv', header = None)

    put_data['spread'] = put_data[put_data.columns[1]] - call_data[call_data.columns[1]]
    del put_data[put_data.columns[1]]

    put_data.to_csv(DATA_DIR +'KOSPI 200 Implied Spread ' + str(put_strike) + '_' + str(call_strike) + '.csv', header = None, index = None)
    
# CONVEXITY SPREAD

strike_put = [100, 95, 90]
strike_call = [100, 105, 110]
spread_list = [10, 15, 20]
  
for put in strike_put:
    strike1 = put
    for spread in spread_list:
        strike2 = strike1 - spread

        put2_data = pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(strike2) + '.csv', header = None)
        put1_data = pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(strike1) + '.csv', header = None)

        put2_data['spread'] = put2_data[put2_data.columns[1]] - put1_data[put1_data.columns[1]]
        del put2_data[put2_data.columns[1]]

        put2_data.to_csv(DATA_DIR +'KOSPI 200 Implied Spread ' + str(strike1) + '_' + str(strike2) + '.csv', header = None, index = None)

for call in strike_call:
    strike1 = call
    for spread in spread_list:
        strike2 = call + spread

        call2_data = pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(strike2) + '.csv', header = None)
        call1_data = pd.read_csv(DATA_DIR +'KOSPI 200 Implied Volatility K' + str(strike1) + '.csv', header = None)

        call1_data['spread'] = call1_data[call1_data.columns[1]] - call2_data[call2_data.columns[1]]
        del call1_data[call1_data.columns[1]]

        call1_data.to_csv(DATA_DIR +'KOSPI 200 Implied Spread ' + str(strike1) + '_' + str(strike2) + '.csv', header = None, index = None)

