import backtrader as bt
from datetime import datetime
import math
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Sizers Testing')


    parser.add_argument('--commperc',
                        default=0.01,
                        type=float,
                        help='The percentage commission to apply to a trade')


    return parser.parse_args()

class maxRiskSizer(bt.Sizer):
    '''
    Restituisce il numero di azioni arrotondate per difetto che possono essere
    acquistate con la massima tolleranza al rischio
    '''
    params = (('risk', 0.1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy == True:
            size = math.floor((cash * self.p.risk) / data[0])
        else:
            size = math.floor((cash * self.p.risk) / data[0]) * -1
        return size


class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):

        if not self.position:
            if self.rsi < 30:
                self.buy()
        elif self.rsi > 70:
            self.close()
        else:
            pass


args = parse_args()

# Variabile con il capitale iniziale
startcash = 10000

# Creare un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungo la strategia
cerebro.addstrategy(firstStrategy)


data = bt.feeds.Quandl(
    dataname='F',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungo i dati finanziari a Cerebro
cerebro.adddata(data)

# Imposto il capitale iniziale
cerebro.broker.setcash(startcash)


cerebro.addsizer(maxRiskSizer)

cerebro.broker.setcommission(commission=args.commperc)

# Esecuzione del backtest
cerebro.run()

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa del risultato finale
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')