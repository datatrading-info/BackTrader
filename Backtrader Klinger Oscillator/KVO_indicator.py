"""
PINE SCRIPT EXAMPLE

//@version=3
study(title="Klinger Oscillator")
sv = change(hlc3) >= 0 ? volume: -volume
kvo = ema(sv, 34) - ema(sv, 55)
sig = ema(kvo, 13)
plot(kvo)
plot(sig, color=green)
"""

import backtrader as bt
from datetime import datetime

class KlingerOsc(bt.Indicator):

    lines = ('sig','kvo')

    params = (('kvoFast',34),('kvoSlow',55),('sigPeriod',13))

    def __init__(self):
        self.plotinfo.plotyhlines = [0]
        self.addminperiod(55)

        self.data.hlc3 = (self.data.high + self.data.low + self.data.close) / 3
        # In backtrader l'indicizazione deve essere () invece che []
        # Vedi: https://www.backtrader.com/docu/concepts.html#lines-delayed-indexing
        self.data.sv = bt.If((self.data.hlc3(0) - self.data.hlc3(-1)) / self.data.hlc3(-1) >=0,
                             self.data.volume, -self.data.volume)
        self.lines.kvo = bt.indicators.EMA(self.data.sv, period=self.p.kvoFast) - bt.indicators.EMA(self.data.sv, period=self.p.kvoSlow)
        self.lines.sig = bt.indicators.EMA(self.lines.kvo, period=self.p.sigPeriod)


class testStrategy(bt.Strategy):

    def __init__(self):
        self.KOsc = KlingerOsc(self.data)


# Creare una instanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(testStrategy)

# Ottenere i dati da Yahoo Finance
data = bt.feeds.Quandl(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True,
    apikey="NBQhvwRzCgdB-6e7XNAD"
    )

# Aggiungere i dati a cerebro
cerebro.adddata(data)

# Esecuzione del backtest
cerebro.run()

# Grafico dei risultati
cerebro.plot(style='candlestick')