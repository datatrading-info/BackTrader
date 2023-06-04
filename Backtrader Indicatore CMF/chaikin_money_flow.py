import backtrader as bt
from datetime import datetime

class MoneyFlow(bt.Indicator):

    lines = ('money_flow',)
    params = (
        ('len', 20),
        )

    plotlines = dict(
        money_flow=dict(
            _name='CMF',
            color='green',
            alpha=0.50
        )
    )

    def __init__(self):
        # Permettere all'indicatore di avere abbastanza dati
        self.addminperiod(self.p.len)

        # Visualizza la linea orizzondale
        self.plotinfo.plotyhlines = [0]

        # Alias per evitare righe troppo lunghe
        c = self.data.close
        h = self.data.high
        l = self.data.low
        v = self.data.volume

        self.data.ad = bt.If(bt.Or(bt.And(c == h, c == l), h == l), 0, ((2*c-l-h)/(h-l))*v)
        self.lines.money_flow = bt.indicators.SumN(self.data.ad, period=self.p.len) / bt.indicators.SumN(self.data.volume, period=self.p.len)


class testStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = MoneyFlow(self.data)

# Creare un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(testStrategy)

# Ottenere i dati di Yahoo Finance.
data = bt.feeds.Quandl(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungere i dati a Cerebro
cerebro.adddata(data)

# Esecuzione del backtest
cerebro.run()

# Grafico dei risultati
cerebro.plot(style='candlestick')