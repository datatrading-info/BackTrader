import backtrader as bt
from datetime import datetime
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries

# IMPORTANTE!
# ----------
# Registrare per un API su:
# https://www.alphavantage.co/support/#api-key
# e inserirla qui
Apikey = 'INSERT YOUR API KEY'


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


def alpha_vantage_daily_adjusted(symbol_list, compact=False, debug=False, rounding=4, *args, **kwargs):
    '''
    Funzione per scaricare i dati di Alpha Vantage.

    Si prevede di restituire una lista nidificato contenente un dataframe pandas e il nome del feed.
    '''
    data_list = list()

    size = 'compact' if compact else 'full'

    for symbol in symbol_list:

        if debug:
            print('Downloading: {}, Size: {}'.format(symbol, size))

        # Inviare la chiare API e creare una sessione
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        # Download dei dati
        data, meta_data = alpha_ts.get_daily_adjusted(symbol=symbol, outputsize=size)
        # data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        if debug:
            print(data)

        # Convertire l'indice in datetime.
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)

        # Correggere il resto dei dati
        data['adj open'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                                data['1. open'], rounding=rounding)
        data['adj high'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                                data['2. high'], rounding=rounding)
        data['adj low'] = np.vectorize(adjust)(data.index.date, data['4. close'], data['5. adjusted close'],
                                               data['3. low'], rounding=rounding)

        # Estrazione delle colonne con cui vogliamo lavoare e le rinominiamo.
        data = data[['adj open', 'adj high', 'adj low', '5. adjusted close', '6. volume']]
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        data['Datetime'] = data.index

        data_list.append((data, symbol))

    return data_list


class RebalanceStrategy(bt.Strategy):
    params = (('assets', list()),
              ('rebalance_months', [1, 6]),)  # Float: 1 == 100%

    def __init__(self):
        self.rebalance_dict = dict()
        for i, d in enumerate(self.datas):
            self.rebalance_dict[d] = dict()
            self.rebalance_dict[d]['rebalanced'] = False
            for asset in self.p.assets:
                if asset[0] == d._name:
                    self.rebalance_dict[d]['target_percent'] = asset[1]

    def next(self):

        for i, d in enumerate(self.datas):
            dt = d.datetime.datetime()
            dn = d._name
            pos = self.getposition(d).size

            if dt.month in self.p.rebalance_months and self.rebalance_dict[d]['rebalanced'] == False:
                print('{} Sending Order: {} | Month {} | Rebalanced: {} | Pos: {}'.format(dt, dn, dt.month,
                                                                                          self.rebalance_dict[d][
                                                                                              'rebalanced'], pos))
                self.order_target_percent(d, target=self.rebalance_dict[d]['target_percent'] / 100)
                self.rebalance_dict[d]['rebalanced'] = True

            # Reset
            if dt.month not in self.p.rebalance_months:
                self.rebalance_dict[d]['rebalanced'] = False

    def notify_order(self, order):
        date = self.data.datetime.datetime().date()

        if order.status == order.Completed:
            print('{} >> Order Completed >> Stock: {},  Ref: {}, Size: {}, Price: {}'.format(

                date,
                order.data._name,
                order.ref,
                order.size,
                'NA' if not order.price else round(order.price, 5)
            ))

    def notify_trade(self, trade):
        date = self.data.datetime.datetime().date()
        if trade.isclosed:
            print('{} >> Notify Trade >> Stock: {}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                date,
                trade.data._name,
                trade.price,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2)))


startcash = 10000

# Crea un istanza dicerebro
cerebro = bt.Cerebro()

# Paramentri della strategia
strat_params = [
    ('SPY', 30),
    ('IWM', 30),
    ('TIP', 20),
    ('TLT', 20)
]

symbol_list = [x[0] for x in strat_params]

# Aggiungere la strategia
cerebro.addstrategy(RebalanceStrategy, assets=strat_params)

data_list = alpha_vantage_daily_adjusted(
    symbol_list,
    compact=False,
    debug=True)

for i in range(len(data_list)):
    data = bt.feeds.PandasData(
        dataname=data_list[i][0],  # Pandas DataFrame
        name=data_list[i][1],  # Symbol
        timeframe=bt.TimeFrame.Days,
        compression=1,
        fromdate=datetime(2014, 1, 1),
        todate=datetime(2020, 1, 1)
    )

    # Aggiungere i dati a Cerebro
    cerebro.adddata(data)

# Impostare il capitale iniziale
cerebro.broker.setcash(startcash)
cerebro.broker.set_checksubmit(False)

# Esecuzione del backtest
cerebro.run()

# Ottenere il valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')