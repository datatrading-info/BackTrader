import backtrader as bt
from datetime import datetime

class rsiStrategy(bt.Strategy):
    params = (
        ('period',21),
        )

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < 30: self.buy(size=100)
            else:
                if self.rsi > 70:
                    self.sell(size=100)

    def stop(self):
        pnl = round(self.broker.getvalue() - self.startcash,2)
        print('RSI Period: {} Final PnL: {}'.format(
            self.params.period, pnl))

if __name__ == '__main__':
    # Variabile per il capitale iniziale
    startcash = 10000

    # Creare un'istanza di cerebro
    cerebro = bt.Cerebro()

    # Aggiungere la strategia
    cerebro.optstrategy(rsiStrategy, period=range(14,21))

    # Download dei dati di Apple da Yahoo Finance.
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        fromdate = datetime(2016,1,1),
        todate = datetime(2017,1,1),
        buffered= True
        )

    # Aggiungere i dati di Apple a Cerebro
    cerebro.adddata(data)

    # Impostare il capitale iniziale
    cerebro.broker.setcash(startcash)

    # Esecuzione
    strats = cerebro.run()