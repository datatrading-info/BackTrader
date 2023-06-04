import backtrader as bt
from datetime import datetime
import signal


class sigStrategy(bt.Strategy):

    def __init__(self):
        self.count = 0
        signal.signal(signal.SIGINT, self.sigstop)

    def next(self):
        print('{}: O {}, H {}, L {}, C {}'.format(
            self.data.datetime.datetime(),
            self.data.open[0],
            self.data.high[0],
            self.data.low[0],
            self.data.close[0]
        ))

    def sigstop(self, a, b):
        print('Stopping Backtrader')
        self.env.runstop()


apikey = 'INSERT YOUR API KEY'
acc = 'INSERT YOUR ACC NUM'
inst = 'GBP_USD'

# Creo un istanza di cerebro
cerebro = bt.Cerebro()

# Setup Oanda
oandastore = bt.stores.OandaStore(token=apikey, account=acc, practice=True)
# broker = oandastore.getbroker()
# cerebro.setbroker(broker)

data = oandastore.getdata(dataname=inst, backfill_start=True, timeframe=bt.TimeFrame.Ticks, compression=1)
# Sostituisco i dati nell'ambiente di test così possiamo agire più velocemente
cerebro.resampledata(data, name=inst, timeframe=bt.TimeFrame.Minutes, compression=1)

# Aggiungo la strategia
cerebro.addstrategy(sigStrategy)

# Esecuzione del motore
cerebro.run()

# Grafico dei risultati
cerebro.plot(style='candlestick')