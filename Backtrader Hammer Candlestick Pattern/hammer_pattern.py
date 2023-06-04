

from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime

# IMPORTANTE!
# ----------
# Registrare per un API su:
# https://www.alphavantage.co/support/#api-key
# e inserirla qui
Apikey = 'INSERT YOUR API KEY HERE'


class HammerCandles(bt.Indicator):
    '''
    Indicatore della candela d'inversione che prova a cattuare gli swing
    e cavalcare il ritracciamento.
    '''
    lines = ('signal','bull_hammer', 'bear_hammer')
    params = (
        ('rev_wick_ratio', 0.6), # rapporto dello spike
    )

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True
    )
    plotlines = dict(
        bull_hammer=dict(marker='^', markersize=8.0, color='blue', fillstyle='full', ls='',
        ),
        bear_hammer=dict(marker='v', markersize=8.0, color='orange', fillstyle='full', ls='',
        ),
        signal=dict(_plotskip=True)
    )

    def __init__(self):
        pass

    def next(self):

        # Controllo il range
        range = round(self.data.high - self.data.low,5)

        # Calcola il rapporto per le candele verdi o se open = close
        if self.data.open <= self.data.close:

            upper_wick = round(self.data.high - self.data.close,5)
            lower_wick = round(self.data.open - self.data.low,5)

            try:
                upper_ratio = round(upper_wick/range,5)
            except ZeroDivisionError:
                upper_ratio = 0

            try:
                lower_ratio = round(lower_wick/range,5)
            except ZeroDivisionError:
                lower_ratio = 0

        # Calcolo rapporto per le candele rosse
        elif self.data.open > self.data.close:

            upper_wick = round(self.data.high - self.data.open,5)
            lower_wick = round(self.data.close - self.data.low,5)

            try:
                upper_ratio = round(upper_wick/range,5)
            except ZeroDivisionError:
                upper_ratio = 0

            try:
                lower_ratio = round(lower_wick/range,5)
            except ZeroDivisionError:
                lower_ratio = 0


        if upper_ratio >= self.p.rev_wick_ratio:

            self.lines.bear_hammer[0] = self.data.high[0]
            self.lines.signal[0] = -1

        elif lower_ratio >= self.p.rev_wick_ratio:

            self.lines.bull_hammer[0] = self.data.low[0]
            self.lines.signal[0] = 1

        else:
            self.lines.signal[0] = 0


def alpha_vantage_eod(symbol_list, compact=False, debug=False, *args, **kwargs):
    '''
        funzione helper per scaricare i dati di Alpha Vantage.

        Restituisce una lista nidificata dove ogni elemento contiene:
            [0] dataframe di pandas
            [1] il nome del datafeed
        '''
    data_list = list()

    size = 'compact' if compact else 'full'

    count = 0
    total = len(symbol_list)

    for symbol in symbol_list:
        count += 1

        print('\nDownloading: {}'.format(symbol))
        print('Symbol: {} of {}'.format(count, total, symbol))
        print('-' * 80)

        # Inviamo l'API e creiamo la sessione
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        # Converire l'indice in datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if debug:
            print(data)

        data_list.append((data, symbol))

    return data_list

class TestStrategy(bt.Strategy):

    def __init__(self):

        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d] = HammerCandles(d)


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


# Crea un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiunge la strategia
cerebro.addstrategy(TestStrategy)

# Scarica di dati da Alpha Vantage.
symbol_list = ['AAPL','MSFT',]
data_list = alpha_vantage_eod(
                symbol_list,
                compact=False,
                debug=False)

for i in range(len(data_list)):

    data = bt.feeds.PandasData(
                dataname=data_list[i][0], # Pandas DataFrame
                name=data_list[i][1], # Symbol
                timeframe=bt.TimeFrame.Days,
                compression=1,
                fromdate=datetime(2018,1,1),
                todate=datetime(2019,1,1)
                )

    # Aggiunge i dati a Cerebro
    cerebro.adddata(data)


print('Starting to run')
# Esecuzione del backtest
cerebro.run()

cerebro.plot(style='candlestick')