
from alpha_vantage.timeseries import TimeSeries
import backtrader as bt
from datetime import datetime
import argparse
import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description='Market Data Downloader')


    parser.add_argument('-s','--symbol',
                        type=str,
                        required=True,
                        help='The Symbol of the Instrument/Currency Pair To Download')


    parser.add_argument('--adjusted',
                        action='store_true',
                        help='Use Adjusted Data')

    parser.add_argument('--rounding',
                        default=4,
                        help='Round adjusted data to nearest x')

    return parser.parse_args()


class testStrategy(bt.Strategy):

    def next(self):
        if not self.position:
            self.order_target_percent(target=1)


def adjust(date, close, adj_close, in_col, rounding=4):
    '''
    Se uso forex o Crypto - Cambia l'arrotondamento!
    '''
    try:
        factor = adj_close / close
        return round(in_col * factor, rounding)
    except ZeroDivisionError:
        print('WARNING: DIRTY DATA >> {} Close: {} | Adj Close {} | in_col: {}'.format(date, close, adj_close, in_col))
        return 0


args = parse_args()

apikey = 'INSERT YOUR API KEY'

# capitale iniziale
startcash = 10000

# creazione istanza di cerebro
cerebro = bt.Cerebro()

# aggiungere la strategia
cerebro.addstrategy(testStrategy)

# Download dei dati di Apple da ALPHA Vantage.
# -------------------------------
# Invio della API e creazione della sessione
alpha_ts = TimeSeries(key=apikey, output_format='pandas')

# Ottenre i dati
if args.adjusted:
    data, meta_data = alpha_ts.get_daily_adjusted(symbol=args.symbol, outputsize='full')

    # Conversione dell'indice in datetime.
    data.index = pd.to_datetime(data.index)

    # NOTA: Pandas Keys = '1. open', '2. high', '3. low', '4. close', '5. adjusted close',
    #                     '6. volume','7. dividend', '8. split coefficient'

    # Aggiustamento del resto dei dati
    data['adj open'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'], data['1. open'], rounding=args.rounding)
    data['adj high'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'], data['2. high'], rounding=args.rounding)
    data['adj low'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'], data['3. low'], rounding=args.rounding)

    # Estrazione e Rinomina delle colonne con cui vogliamo lavoare
    data = data[['adj open', 'adj high', 'adj low','5. adjusted close','6. volume']]
    data.columns = ['Open','High','Low','Close','Volume']

else:

    data, meta_data = alpha_ts.get_daily(symbol=args.symbol, outputsize='full')
    # Conversione dell'indice in datetime.
    data.index = pd.to_datetime(data.index)
    # Rinomina le colonne
    data.columns = ['Open','High','Low','Close','Volume']

# Aggiungere i dati a cerebro
data_in = bt.feeds.PandasData(dataname=data, timeframe=bt.TimeFrame.Days, compression=1)

cerebro.adddata(data_in)

# Impostazione del capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Ottenere il valore finale del portafoglio
portvalue = round(cerebro.broker.getvalue(),2)
pnl = portvalue - startcash

# Stampa del risultato finale
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')