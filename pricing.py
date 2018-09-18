import pandas as pd
import math
from math import log, sqrt, pi, exp
from os.path import dirname, join
import datetime

DATA_DIR = '/home/francois/2trader/'

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

price = 0.00194
strike = 23470.8
fwd = 29338.56
ytm = 0.014244
rates = 0.015
callput = "p"
nbloops = 200
precision = 0.02
minvol = 0.05
maxvol = 0.40


P_theo = 100 * option_price(strike/100, fwd/100, ytm, rates, callput, 0.185)
print(P_theo)

V_theo = implied_vol(price/100, strike/100, fwd/100, ytm, rates, callput, nbloops, precision, minvol, maxvol)
print(V_theo[1])