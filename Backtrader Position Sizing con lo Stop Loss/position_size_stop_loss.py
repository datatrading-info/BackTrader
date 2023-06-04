
import backtrader as bt
from datetime import datetime
import math

class TestStrategy(bt.Strategy):

    params = (('risk', 0.1), #risk 10%
        ('stop_dist', 0.05)) #stoploss distance 5%

    def next(self):
        date = self.data.datetime.date()
        bar = len(self)
        cash = self.broker.get_cash()

        if bar == 7:
            stop_price = (self.data.close[0] * (1 - self.p.stop_dist))
            qty = math.floor((cash * self.p.risk) / (self.data.close[0] - stop_price))
            self.buy(size=qty)
            self.sell(exectype=bt.Order.Stop, size=qty, price=stop_price)


    def notify_trade(self, trade):
        date = self.data.datetime.datetime()
        if trade.isclosed:
            print('-'*32,' NOTIFY TRADE ','-'*32)
            print('{}, Avg Price: {}, Profit, Gross {}, Net {}'.format(
                                                date,
                                                trade.price,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
            print('-'*80)

startcash = 10000

# Creare un'istanza di celebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(TestStrategy)

# Impostare le commissioni
cerebro.broker.setcommission(leverage=20)

# Creare il datafeed
data = bt.feeds.GenericCSVData(
    timeframe=bt.TimeFrame.Days,
    compression=1,
    dataname='data/PositionSizingTestData.csv',
    nullvalue=0.0,
    dtformat=('%m/%d/%Y'),
    datetime=0,
    time=-1,
    high=2,
    low=3,
    open=1,
    close=4,
    volume=-1,
    openinterest=-1 #-1 means not used
    )

# Aggiungere i dati
cerebro.adddata(data)

# Imposto il capitale inziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))
print('P/L: {}%'.format(((portvalue - startcash)/startcash)*100))

# Grafico dei risultati
cerebro.plot(style='candlestick')