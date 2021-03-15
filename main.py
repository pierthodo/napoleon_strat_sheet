import pandas as pd
import requests
import datetime
import quantstats as qs
import matplotlib.font_manager
import pandas_datareader as pdr
import os
import pdfkit

# extend pandas functionality with metrics, etc.
qs.extend_pandas()
def get_napbots(strat):
    response = requests.get('https://middle.napbots.com/v1/strategy/details/'+strat)
    key = list(response.json()['data']['performance']['quotes'].keys())[0]
    price = [[datetime.datetime.strptime(i['date'], '%Y-%m-%d'),float(i['last'])] for i in response.json()['data']['performance']['quotes'][key]]
    df = pd.DataFrame(price,columns=["Date","Price"])
    df['Date'] = pd.to_datetime(df['Date'],utc=False)
    df.set_index('Date', inplace=True)
    #qs.plots.snapshot(df["Price"].squeeze(),title="Strat")
    return df
def get_crypto(pair):
    df_btc = pdr.get_data_yahoo([pair],
                          start=datetime.datetime(2017, 1, 1),
                          end=datetime.datetime.now())['Close']
    df_btc = df_btc[~df_btc.index.duplicated(keep='first')]
    df_btc["Price"] = df_btc[pair]
    return df_btc

options_strat = [
                {'label': 'NapoX medium term TF BTC LO', 'value': 'STRAT_BTC_USD_D_3'},
                {'label': 'NapoX medium term TF ETH LO', 'value': 'STRAT_ETH_USD_D_3'},
                {'label': 'NapoX BTC Ultra flex AR hourly', 'value': 'STRAT_BTC_USD_H_3_V2'},
                {'label': 'NapoX ETH Ultra flex AR hourly', 'value': 'STRAT_ETH_USD_H_3_V2'},
                {'label': 'NapoX alloc ETH/BTC/USD AR hourly', 'value': 'STRAT_BTC_ETH_USD_H_1'},
                {'label': 'NapoX alloc ETH/BTC/USD LO hourly', 'value': 'STRAT_BTC_ETH_USD_LO_H_1'},
                 {'label': 'NapoX alloc ETH/BTC/USD AR daily', 'value': 'STRAT_BTC_ETH_USD_D_1_V2'},
                 {'label': 'NapoX alloc ETH/BTC/USD LO daily', 'value': 'STRAT_BTC_ETH_USD_LO_D_1'}
                 ]
options_crypto = [{'label': 'BTC-USD', 'value': 'BTC-USD'},
                {'label': 'ETH-USD', 'value': 'ETH-USD'},
                 ]
path="./strat_sheet/"
for dic_strat in options_strat:
    path_strat = path+dic_strat["label"]
    if not os.path.exists(path_strat):
        os.makedirs(path_strat)
    for bench in ["ETH-USD", "BTC-USD"]:
        path_bench = path_strat + "/" + bench
        if not os.path.exists(path_bench):
            os.makedirs(path_bench)
        strat = get_napbots(dic_strat["value"])
        benchmark = get_crypto(bench)
        for timeframe in [30,90,180,360,720,1040]:
            print("Done")

            path_time = path_bench+"/"+str(timeframe)+ "-days.html"
            try:
                report = qs.reports.html(strat["Price"].squeeze()[-timeframe:], benchmark["Price"].squeeze()[-timeframe:],
                                         output=path_time)
            except:
                print("Failed with timeframe",timeframe)
            pdfkit.from_file(path_time, path_time[:-5] + ".pdf")

            break
        break
    break

