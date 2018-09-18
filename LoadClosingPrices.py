import math

"""
Generate the bash commad to load option price data using fair-dump function:

example:

rm -f data.csv &&  release/bin/fair-dump -p KSEKospi200 -b 20170501 -e 20171026 -t 0900 -t 1530 
0.6p 0.6c 0.65p 0.65c 0.7p 0.7c 0.75p 0.75c 0.8p 0.8c 0.85p 0.85c 0.9p 0.9c 0.95p 0.95c 1.0p 1.0c 1.05p 
1.05c 1.1p 1.1c 1.15p 1.15c 1.2p 1.2c 1.25p 1.25c 1.3p 1.3c 1.35p 1.35c 1.4p 1.4c >> data.csv

#fair-dump [STRIKES]
  -p FINPROD   --product=FINPROD    financial product
  -b YYYYMMDD  --begin=YYYYMMDD     beginning date
  -e YYYYMMDD  --end=YYYYMMDD       end date
  -t HH:MM:SS  --time=HH:MM:SS      local time of day (high-noon by default)
               --influx-host=HOST   InfluxDB host
  -a           --absolute           Show prices divided by the spot
               --pendula[=PENDULA]  Show pendulum values or specify pendula
  -j PATH      --journal=PATH       TLog source
               --quantile           show moneyness quantiles

Dump data in a open_change.csv file.

THE DATABASE ONLY RETRIEVES DATA FROM 2016-02-24

"""

def Generatecommand():
    #Define Strike Range
    kstart = 60
    kend = 140
    step = 5
    #Define Date Range
    startdate = 20160224
    enddate = 20180911

    load_time = "15:00:00"

    # Genereate the number of strikes
    strikes = []
    ksize = int((kend - kstart) / step + 1)

    for i in range(ksize):
        k = int(kstart + i * step)
        strikes.append(k)

    # Create the command line
    bash = " release/bin/fair-dump -p KSEKospi200 -b " + str(startdate) + " -e " + str(enddate) + " -t " + load_time
    for i in range(ksize):
        if strikes[i] >= 100:
            bash = bash + " " + str(strikes[i]) + "%c "
        else:
            bash = bash + " " + str(strikes[i]) + "%p "

    bash = "rm -f kospi_closing_prices.csv && " + bash + " >> kospi_closing_prices.csv"

    print(bash)

Generatecommand()


