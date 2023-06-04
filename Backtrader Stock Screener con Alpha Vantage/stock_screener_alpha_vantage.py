from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np
import backtrader as bt
from datetime import datetime
import time

# IMPORTANTE!
# ----------
# Registrare per un API su:
# https://www.alphavantage.co/support/#api-key
# e inserirla qui
Apikey = 'INSERT YOUR API KEY HERE'

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
        print('-'*80)

        # Inviamo l'API e creiamo la sessione
        alpha_ts = TimeSeries(key=Apikey, output_format='pandas')

        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)

        # Converire l'indice in datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['Open', 'High', 'Low', 'Close','Volume']

        if debug:
            print(data)

        data_list.append((data, symbol))

        # Pausa per evitare di raggiungere i limiti dell'API
        print('Sleeping |', end='', flush=True)
        for x in range(12):
            print('=', end='', flush=True)
            time.sleep(1)
        print('| Done!')

    return data_list

class TestStrategy(bt.Strategy):

    def __init__(self):

        self.inds = dict()
        self.inds['RSI'] = dict()
        self.inds['SMA'] = dict()

        for i, d in enumerate(self.datas):

            # Per ogni indicatore monitoriamo il suo valore e se è rialzista o
            # ribassista. Possiamo farlo creando una nuova riga che restituisca vero o falso.

            # RSI
            self.inds['RSI'][d._name] = dict()
            self.inds['RSI'][d._name]['value']  = bt.indicators.RSI(d, period=14)
            self.inds['RSI'][d._name]['bullish'] = self.inds['RSI'][d._name]['value']  > 50
            self.inds['RSI'][d._name]['bearish'] = self.inds['RSI'][d._name]['value']  < 50

            # SMA
            self.inds['SMA'][d._name] = dict()
            self.inds['SMA'][d._name]['value']  = bt.indicators.SMA(d, period=20)
            self.inds['SMA'][d._name]['bullish'] = d.close > self.inds['SMA'][d._name]['value']
            self.inds['SMA'][d._name]['bearish'] = d.close < self.inds['SMA'][d._name]['value']

    def stop(self):
        '''
        Chiamato quando backtrader ha terminato il backtest.
        Ricaviamo i valori finali alla fine del test per ciascun indicatore.
        '''

        # Supponendo che tutti i simboli avranno gli stessi dati negli stessi giorni.
        # Se questo non è il caso e si mescolano asset di diverse classi, regioni
        # o exchanges, allora prendere in considerazione l'aggiunta di una colonna in
        # più nei risultati finali.
        print('{}: Results'.format(self.datas[0].datetime.date()))
        print('-'*80)


        results = dict()
        for key, value in self.inds.items():
            results[key] = list()

            for nested_key, nested_value in value.items():

                if nested_value['bullish'] == True or nested_value['bearish'] == True:
                    results[key].append([nested_key, nested_value['bullish'][0],
                            nested_value['bearish'][0], nested_value['value'][0]])


        # Crea e stamp l'intestazione
        headers = ['Indicator','Symbol','Bullish','Bearish','Value']
        print('|{:^10s}|{:^10s}|{:^10s}|{:^10s}|{:^10s}|'.format(*headers))
        print('|'+'-'*10+'|'+'-'*10+'|'+'-'*10+'|'+'-'*10+'|'+'-'*10+'|')

        # Ordina e stampa le rige
        for key, value in results.items():
            #print(value)
            value.sort(key= lambda x: x[0])

            for result in value:
                print('|{:^10s}|{:^10s}|{:^10}|{:^10}|{:^10.2f}|'.format(key, *result))


# Crea un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiunge la strategia
cerebro.addstrategy(TestStrategy)

# Scarica di dati da Alpha Vantage.
symbol_list = ['AAPL','MSFT','AMZN', 'GOOGL']
data_list = alpha_vantage_eod(
                symbol_list,
                compact=True,
                debug=False)

for i in range(len(data_list)):

    data = bt.feeds.PandasData(
                dataname=data_list[i][0], # Pandas DataFrame
                name=data_list[i][1], # Symbol
                timeframe=bt.TimeFrame.Days,
                compression=1
                )

    # Aggiunge i dati a Cerebro
    cerebro.adddata(data)

print('\nStarting Analysis')
print('-'*80)

# Esegue il backtest
cerebro.run()