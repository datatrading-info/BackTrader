from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime

# IMPORTANTE!
# ----------
# Registrarsi per ottenere una chiave API:
# https://www.alphavantage.co/support/#api-key
# e inserirla qui.
Apikey = 'INSERT YOUR API KEY HERE'

def alpha_vantage_eod(symbol_list, compact=False, debug=False, *args, **kwargs):
    '''
    Funzioni che scarica i dati di Alpha Vantage

    Restituisce una lista di oggetti dove ogni elemento contiene:
        [0] dataframe pandas
        [1] il nome del feed.
    '''
    data_list = list()

    size = 'compact' if compact else 'full'

    for symbol in symbol_list:

        if debug:
            print('Downloading: {}, Size: {}'.format(symbol, size))

        # Invia la API key e crea una sessione
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        # Converte l'indice in un datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['Open', 'High', 'Low', 'Close','Volume']
        data.sort_index(inplace=True)

        if debug:
            print(data)

        data_list.append((data, symbol))

    return data_list

class TestStrategy(bt.Strategy):

    def __init__(self):

        pass

    def next(self):

        for i, d in enumerate(self.datas):

            bar = len(d)
            dt = d.datetime.datetime()
            dn = d._name
            o = d.open[0]
            h = d.high[0]
            l = d.low[0]
            c = d.close[0]
            v = d.volume[0]

            print('{} Bar: {} | {} | O: {} H: {} L: {} C: {} V:{}'.format(dt, bar,dn,o,h,l,c,v))


# Crea un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiunge la strategia
cerebro.addstrategy(TestStrategy)

# Scarica i dati da Alpha Vantage.
symbol_list = ['AAPL','MSFT']
data_list = alpha_vantage_eod(
                symbol_list,
                compact=False,
                debug=False)

for i in range(len(data_list)):

    data = bt.feeds.PandasData(
                dataname=data_list[i][0], # Pandas DataFrame
                name=data_list[i][1], # Simbolo
                timeframe=bt.TimeFrame.Days,
                compression=1,
                fromdate=datetime(2018, 1, 1),
                todate=datetime(2019, 1, 1)
                )

    # Aggiungere i dati a cerebro
    cerebro.adddata(data)

print('Starting to run')

# Esecuzione del backtest
cerebro.run()