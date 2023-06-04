
import backtrader as bt
from datetime import datetime
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Argparse Example program\
                        for backtesting')

    parser.add_argument('instrument',
                        help='The yahoo ticker of the instrument being tested')

    parser.add_argument('start',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('end',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('-p', '--period',
                        default=21,
                        type=int,
                        help='Select the RSI lookback period')

    parser.add_argument('-r', '--rsi',
                        choices=['SMA', 'EMA'],
                        help='Select wether a simple moving average or exponential\
                         moving average is used in the RSI calcuation')

    return parser.parse_args()


class firstStrategy(bt.Strategy):
    params = (
        ('rsi', 'SMA'),
        ('period', 21),
    )

    def __init__(self):
        if self.p.rsi == 'EMA':
            self.rsi = bt.indicators.RSI_EMA(self.data.close, period=self.p.period)
        else:
            self.rsi = bt.indicators.RSI_SMA(self.data.close, period=self.p.period)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)


# Ottengo gli argomenti
args = parse_args()

# Converto gli argomenti date in oggetti datetime
fd = datetime.strptime(args.start, '%Y-%m-%d')
td = datetime.strptime(args.end, '%Y-%m-%d')

# Capitale iniziale
startcash = 10000

# Creo un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungo la strategia
cerebro.addstrategy(firstStrategy, rsi=args.rsi, period=args.period)

# Download dei dati Apple da Yahoo Finance.
data = bt.feeds.YahooFinanceData(
    dataname=args.instrument,
    fromdate=fd,
    todate=td,
    buffered=True
)

# Aggiungo i dati di Apple a Cerebro
cerebro.adddata(data)

# imposto il capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')