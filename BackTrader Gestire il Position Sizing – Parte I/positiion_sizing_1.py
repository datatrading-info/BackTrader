import backtrader as bt
from datetime import datetime
import math


class exampleSizer(bt.Sizer):
    params = (('size',1),)
    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.p.size

class printSizingParams(bt.Sizer):
    '''
    Stampa i parametri di sizing e i valori restituiti dai metodi della classe
    '''
    def _getsizing(self, comminfo, cash, data, isbuy):
        # esempio metodi della classe Strategy
        pos = self.strategy.getposition(data)
        # esempio medoti della classe Broker
        acc_value = self.broker.getvalue()

        # stampa risultati
        print('----------- SIZING INFO START -----------')
        print('--- Strategy method example')
        print(pos)
        print('--- Broker method example')
        print('Account Value: {}'.format(acc_value))
        print('--- Param Values')
        print('Cash: {}'.format(cash))
        print('isbuy??: {}'.format(isbuy))
        print('data[0]: {}'.format(data[0]))
        print('------------ SIZING INFO END------------')

        return 0

class maxRiskSizer(bt.Sizer):
    '''
    Restituisce il numero approssimato per difetto di azioni che possono essere
    acquistati con il massimo della tolleranza al rischio
    '''
    params = (('risk', 0.03),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('Il parametro Risk è una percentuale che deve essere valorizzata come un float. es. 0.5')

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
            else:
                if self.rsi > 70:
                    self.close()

    def notify_trade(self, trade):
        if trade.justopened:
            print('----TRADE OPENED----')
            print('Size: {}'.format(trade.size))
        elif trade.isclosed:
            print('----TRADE CLOSED----')
            print('Profit, Gross {}, Net {}'.format(
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
        else:
            return


# Capitale iniziale
startcash = 10000

# Creo un istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungo la strategia
cerebro.addstrategy(firstStrategy)

# Download i dati di Apple da Yahoo Finance.
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate = datetime(2016,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungo i dati di Apple a Cerebro
cerebro.adddata(data)

# Imposto il capitale iniziale
cerebro.broker.setcash(startcash)

# Aggiungo il sizer
cerebro.addsizer(printSizingParams)

# Esecuzione del backtest
cerebro.run()

# valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('----SUMMARY----')
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')