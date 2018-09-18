import pandas as pd
import math
from math import log, sqrt

DATA_DIR = '/home/francois/Python/Dashboard/'

def CloseToCloseHistoricalVolatlity(spots, days):

    # number of historical volatilites we can compute
    N = len(spots) - days
    volatility = []
    for i in range(N):
        # for each computation of volatility
        sumlogreturns = 0
        for j in range(days):
            sumlogreturns += log(float(spots[i + j])/float(spots[i +j + 1])) **2

        volatility.append(100 * sqrt(252 * sumlogreturns / (days -1)))

    return volatility

def ParkinsonHistoricalVolatility(highs, lows, days):

    # number of historical volatilites we can compute
    N = len(highs) - days
    volatility = []
    for i in range(N):
        # for each computa=ln(tion of volatility
        sumlogreturns = 0
        for j in range(days):
            sumlogreturns += log(float(highs[i + j])/float(lows[i + j])) **2

        volatility.append(100 * sqrt(252 * (sumlogreturns / (4 * log(2))) / (days)))

    return volatility

def GarmanKlassHistoricalVolatilities(opens, closes, highs, lows, days):

    # number of historical volatilites we can compute
    N = len(highs) - days
    volatility = []
    for i in range(N):
        # for each computa=ln(tion of volatility
        sumlogreturns_oc = 0
        sumlogreturns_hl = 0
        for j in range(days):
            sumlogreturns_hl += log(float(highs[i + j])/float(lows[i + j])) **2
            sumlogreturns_oc += log(float(closes[i + j])/float(opens[i + j])) **2

        volatility.append(100 * sqrt( (252 / days) * (0.5 * sumlogreturns_hl - (2 * log(2) - 1) * sumlogreturns_oc)))

    return volatility

def RogersSatchellHistoricalVolatilities(opens, closes, highs, lows, days):

    # number of historical volatilites we can compute
    N = len(highs) - days
    volatility = []
    for i in range(N):
        # for each computa=ln(tion of volatility
        sumlogreturns_h = 0
        sumlogreturns_l = 0
        for j in range(days):
            sumlogreturns_h += log(float(highs[i + j])/float(closes[i + j])) * log(float(highs[i + j])/float(opens[i + j]))
            sumlogreturns_l += log(float(lows[i + j])/float(closes[i + j])) * log(float(lows[i + j])/float(opens[i + j]))

        volatility.append(100 * sqrt( (252 / days) * (sumlogreturns_l + sumlogreturns_h)))

    return volatility

def GarmanKlassYangZhangHistoricalVolatilities(opens, closes, highs, lows, days):

    # number of historical volatilites we can compute
    N = len(highs) - days
    volatility = []
    for i in range(N):
        # for each computa=ln(tion of volatility
        sumlogreturns_oc1 = 0
        sumlogreturns_hl  = 0
        sumlogreturns_oc  = 0
        for j in range(days):
            sumlogreturns_oc1 += log(float(opens[i + j])/float(closes[i + j + 1])) **2
            sumlogreturns_hl  += log(float(highs[i + j])/float(lows[i + j])) **2
            sumlogreturns_oc  += log(float(closes[i + j])/float(opens[i + j])) **2

        volatility.append(100 * sqrt( (252 / days) * (sumlogreturns_oc1 + 0.5 * sumlogreturns_hl - (2 * log(2) - 1) * sumlogreturns_oc )))

    return volatility

# get data from csv file
data = pd.read_csv(DATA_DIR + "KOSPI 200 Historical Data.csv")

# get data and move them into lists of values
closes = data['Price'].values.tolist()
opens  = data['Open'].values.tolist()
dates  = data['Date'].values.tolist()
highs  = data['High'].values.tolist()
lows   = data['Low'].values.tolist()
volume = data['Vol.'].values.tolist()

# let's compute the historical volatilities

for days in [5, 15, 30]:

    closehistovols     = CloseToCloseHistoricalVolatlity(closes, days)
    parkhistovols      = ParkinsonHistoricalVolatility(highs,lows,days)
    garmanklassvols    = GarmanKlassHistoricalVolatilities(opens, closes, highs, lows, days)
    rogerssatchellvols = RogersSatchellHistoricalVolatilities(opens, closes, highs, lows, days)
    garmanklasszyvols  = GarmanKlassYangZhangHistoricalVolatilities(opens, closes, highs, lows, days)

    CC_data = pd.DataFrame(closehistovols, dates[:-days])
    PK_data = pd.DataFrame(parkhistovols, dates[:-days])
    GK_data = pd.DataFrame(garmanklassvols,dates[:-days]) 
    RS_data = pd.DataFrame(rogerssatchellvols, dates[:-days])
    GY_data = pd.DataFrame(garmanklasszyvols, dates[:-days])

    CC_data.to_csv(DATA_DIR+ 'KOSPI 200 Historical Volatility CC' + str(days) + 'D.csv', header = None)
    PK_data.to_csv(DATA_DIR+ 'KOSPI 200 Historical Volatility PK' + str(days) + 'D.csv', header = None)
    GK_data.to_csv(DATA_DIR+ 'KOSPI 200 Historical Volatility GK' + str(days) + 'D.csv', header = None)
    RS_data.to_csv(DATA_DIR+ 'KOSPI 200 Historical Volatility RS' + str(days) + 'D.csv', header = None)
    GY_data.to_csv(DATA_DIR+ 'KOSPI 200 Historical Volatility GY' + str(days) + 'D.csv', header = None)

