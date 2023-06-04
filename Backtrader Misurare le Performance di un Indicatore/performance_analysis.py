import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime
import argparse
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description="COT BACKTESTER")

    parser.add_argument('--data',
                        default='data/EUR_USD-D.csv',
                        type=str,
                        help='Price Data CSV File')

    parser.add_argument('--results',
                        default='SignalAnalysis-Results.csv',
                        type=str,
                        help='Price Data CSV File')

    parser.add_argument('--bars',
                        default=200,
                        type=int,
                        help='Analyze the following x bars')

    parser.add_argument('--period',
                        default=200,
                        type=int,
                        help='SMA Lookback Period')

    parser.add_argument('--analyze_only',
                        action='store_true',
                        help='Perform Pandas Analysis Only')

    return parser.parse_args()


class SignalAnalysis(bt.Strategy):

    params = (
        ('sma_lkb', 200),
        )

    def __init__(self):

        self.setup_log_file()
        # Indicatore
        self.sma = bt.indicators.SMA(self.data, period=self.p.sma_lkb)
        self.cross = bt.indicators.CrossOver(self.data.close, self.sma)

    def next(self):
        dt = self.datas[0].datetime.datetime()
        bar = len(self.datas[0])
        o = self.datas[0].open[0]
        h = self.datas[0].high[0]
        l = self.datas[0].low[0]
        c = self.datas[0].close[0]
        v = self.datas[0].volume[0]

        # Crea alcuni alias dei segnale in modo da poterli sostituire facilmente
        # con migliori segnali in un secondo momento
        long = self.cross == 1
        short = self.cross == -1

        # Questa parte può essere trascurata
        # Basta creare le condizioni long e short nelle righe precedenti!
        if long:
            sig = 'Long'
        elif short:
            sig = 'Short'
        else:
            sig = ''

        with open(self.logfile, 'a+') as f:
            log = "{},{},{},{},{},{},{}\n".format(dt,o,h,l,c,v,sig)
            f.write(log)


    def setup_log_file(self):
        '''
        Funzione per impostare i file di log
        '''
        cn = self.__class__.__name__
        self.logfile ='{}-Results.csv'.format(cn)

        # Scrive l'header nel log dei trade.
        log_header = 'Datetime,Open,High,Low,Close,Volume,Signal'

        with open(self.logfile, 'w') as file:
            file.write(log_header + "\n")


args = parse_args()

if not args.analyze_only:
    # Creare un istanza di cerebro
    cerebro = bt.Cerebro()

    # Aggiungere la strategia
    cerebro.addstrategy(SignalAnalysis, sma_lkb=args.period)

    # Creare il DataFeed
    data = bt.feeds.GenericCSVData(
        timeframe=bt.TimeFrame.Days,
        compression=1,
        dataname=args.data,
        nullvalue=0.0,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        datetime=0,
        time=-1,
        high=2,
        low=3,
        open=1,
        close=4,
        volume=5,
        openinterest=-1 #-1 significa non usato
        )

    cerebro.adddata(data)

    # Esecuzione del backtest
    strats = cerebro.run()



# Creare Dataframe da file CSV
df = pd.read_csv(args.results, parse_dates=True, index_col=[0])

# Ottenere le date dei segnali long e short
longs = df[df['Signal'] == 'Long']
shorts = df[df['Signal'] == 'Short']

# Ottenere i valori degli indici per ciascun segnale. Da usare in seguito per
# il looping e la creazione di un nuovo dataframe
long_entries = longs.index.values
short_entries = shorts.index.values

# Creare due nuovi dataframes per i risultati
long_analysis = pd.DataFrame()
short_analysis = pd.DataFrame()


def pnl_calc(x, open_value, short=False):
    '''
    open_value: Float, il valore close della barra del segnale
    short: Bool, invertire il calcolo della percentuale di variazione per gli short
    '''
    try:
        pnl = (x - open_value) / open_value

        if short:
            return -pnl
        else:
            return pnl
    except ZeroDivisionError:
        return 0

for signal_date in long_entries:
    # Ottenere i valori di chiusura per le 200 barre successive al segnale
    closes = pd.DataFrame(df['Close'].loc[signal_date:].head(args.bars + 1),).reset_index()

    # Calcolare la differenza
    closes['PNL'] = closes['Close'].apply(pnl_calc, open_value=closes['Close'].iloc[0], short=False)
    long_analysis[signal_date] = closes['PNL']

for signal_date in short_entries:
    closes = pd.DataFrame(df['Close'].loc[signal_date:].head(args.bars + 1),).reset_index()

    closes['PNL'] = closes['Close'].apply(pnl_calc, open_value=closes['Close'].iloc[0], short=True)
    short_analysis[signal_date] = closes['PNL']

# Ottenre il PNL medio
long_average = long_analysis.mean(axis=1)
short_average = short_analysis.mean(axis=1)

# Grafici
# ------------------------------------------------------------------------------
fig, axes = plt.subplots(nrows=2, ncols=2)

# Tutte le entrate long
ax1 = long_analysis.plot(ax=axes[0,0], kind='line', legend=False, title='Long Signal PnL / Bar', )
ax1.set_ylabel("PnL %")

# Tutte le entrate short
ax2 = short_analysis.plot(ax=axes[0,1], kind='line',  legend=False, title='Short Signal PnL / Bar')
ax2.set_ylabel("PnL %")

# Media delle entrate long
ax3 = long_average.plot(ax=axes[1,0], kind='line', legend=False, title='Long Average')
ax3.set_xlabel("Bar No")

# Media delle entrate short
ax4 = short_average.plot(ax=axes[1,1], kind='line', legend=False, title='Short Average')
ax4.set_xlabel("Bar No")

fig.set_size_inches(10.5, 6.5)

# Grafico
plt.show()