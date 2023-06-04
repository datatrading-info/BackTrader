import backtrader as bt
from datetime import datetime

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
            else:
                if self.rsi > 70:
                    self.sell(size=100)


# Variabile per il capitale iniziale
startcash = 10000

# crea un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiunge la strategia
cerebro.addstrategy(firstStrategy)

# Download dei dati di Apple da Yahoo Finance.
data = bt.feeds.Quandl(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungi i dati di Apple a Cerebro
cerebro.adddata(data)

# Imposta il capitale iniziale
cerebro.broker.setcash(startcash)