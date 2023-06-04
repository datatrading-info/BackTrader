import backtrader as bt
from datetime import datetime
from extensions.indicators import SwingInd

class simpleStrategy(bt.Strategy):

    def __init__(self):
        self.piv = SwingInd(period=7)

# Crea un'istanza di cerebro
cerebro = bt.Cerebro(stdstats=False)

# Aggiuge la strategia
cerebro.addstrategy(simpleStrategy)

# Download dati di Apple da Yahoo Finance.
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiunge i dat a Cerebro
cerebro.adddata(data)

# Esecuzione della strategia
cerebro.run()

# Stampa del grefico dei risultati
cerebro.plot(style='candlestick')