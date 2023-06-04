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


if __name__ == '__main__':
    # Variabile per il capitale iniziale
    startcash = 10000

    # Creare un'istanza di cerebro
    cerebro = bt.Cerebro(optreturn=False)

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
    opt_runs = cerebro.run()

    # Genera la lista dei risultati
    final_results_list = []
    for run in opt_runs:
        for strategy in run:
            value = round(strategy.broker.get_value(), 2)
            PnL = round(value - startcash, 2)
            period = strategy.params.period
            final_results_list.append([period, PnL])

    # Ordina la lista dei risultati
    by_period = sorted(final_results_list, key=lambda x: x[0])
    by_PnL = sorted(final_results_list, key=lambda x: x[1], reverse=True)

    # Stampa i risultati
    print('Results: Ordered by period:')
    for result in by_period:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))
    print('Results: Ordered by Profit:')
    for result in by_PnL:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))