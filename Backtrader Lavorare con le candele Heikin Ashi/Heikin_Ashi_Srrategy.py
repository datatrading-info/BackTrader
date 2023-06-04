
import backtrader as bt
from datetime import datetime
import math
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Ngyuen: Price/Volume Anomaly Detection Strategy')

    parser.add_argument('--heikin',
                            action ='store_true',
                            help=('Add Heikin Data Filter'))

    parser.add_argument('--debug',
                            action ='store_true',
                            help=('Print Debugs'))

    return parser.parse_args()


class HeikinStrategy(bt.Strategy):

    params = (('debug', False),)

    def next(self):

        if not self.position:
            if self.data.close[0] > self.data.open[0]: # Heikin-Ashi Verde
                self.buy(size=100)
            elif self.data.close[0] < self.data.open[0]: # Heikin-Ashi Rossa
                self.sell(size=100)
            else:
                pass # Chiusura neutrale

        else:
            if self.position.size > 0 and self.data.close[0] < self.data.open[0]: # Heikin-Ashi Rossa
                self.sell(size=200) # Posizione Reverse
            elif self.position.size < 0 and self.data.close[0] > self.data.open[0]: # Heikin-Ashi Verde
                self.buy(size=200) # Posizione Reverse
            else:
                pass

        if self.p.debug:
            print('---------------------------- NEXT ----------------------------------')
            print("1: Data Name:                            {}".format(self.data._name))
            print("2: Bar Num:                              {}".format(len(self.data)))
            print("3: Current date:                         {}".format(self.data.datetime.datetime()))
            print('4: Open:                                 {}'.format(self.data.open[0]))
            print('5: High:                                 {}'.format(self.data.high[0]))
            print('6: Low:                                  {}'.format(self.data.low[0]))
            print('7: Close:                                {}'.format(self.data.close[0]))
            print('8: Volume:                               {}'.format(self.data.volume[0]))
            print('--------------------------------------------------------------------')

    def notify_trade(self,trade):
        if trade.isclosed:
            dt = self.data.datetime.date()
            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl,2)))
            print('--------------------------------------------------------------------')


args = parse_args()

# Capitale iniziale
startcash = 10000

# Creare un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere una strategia
cerebro.addstrategy(HeikinStrategy, debug=args.debug)

data = bt.feeds.Quandl(
    dataname='F',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Filtro sui dati
if args.heikin:
    data.addfilter(bt.filters.HeikinAshi(data))

# Aggiungere i dati a Cerebro
cerebro.adddata(data)

# Impostare il capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Ottenre il valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(round(portvalue,2)))
print('P/L: ${}'.format(round(pnl,2)))

# Grafico dei risultati finali
cerebro.plot(style='candlestick')