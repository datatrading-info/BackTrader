
import backtrader as bt
from datetime import datetime


class Mltests(bt.Strategy):
    '''
    Questa strategia contiene alcuni metodi aggiuntivi che possono essere utilizzati per calcolare
    se una posizione debba essere soggetta a una chiusura con margine da parte di Oanda.
    '''
    params = (('size', 200000),)

    def __init__(self):
        self.count = 0
        self.buybars = [1, 150]
        self.closebars = [100, 250]

    def next(self):
        bar = len(self.data)
        self.dt = self.data.datetime.date()
        if not self.position:
            if bar in self.buybars:
                self.cash_before = self.broker.getcash()
                value = self.broker.get_value()
                entry = self.buy(size=self.p.size)
                entry.addinfo(name='Entry')
        else:
            '''
            Controlla se le condizioni di chiusura del margine sono soddisfatte. 
            In caso contrario, controlla per vedere se dobbiamo chiudere la 
            posizione attraverso le regole della strategia.

            Se si verifica una chiusura, dobbiamo aggiungere informazioni all'ordine 
            in modo che possiamo avere il corretto log
            '''
            mco_result = self.check_mco(
                value=self.broker.get_value(),
                margin_used=self.margin
            )

            if mco_result == True:
                close = self.close()
                close.addinfo(name='MCO')

            elif bar in self.closebars:
                close = self.close()
                close.addinfo(name='Close')

        self.count += 1

    def notify_trade(self, trade):
        if trade.isclosed:
            print('{}: Trade closed '.format(self.dt))
            print('{}: PnL Gross {}, Net {}\n\n'.format(self.dt,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))

    def notify_order(self,order):
        if order.status == order.Completed:
            ep = order.executed.price
            es = order.executed.size
            tv = ep * es
            leverage = self.broker.getcommissioninfo(self.data).get_leverage()
            self.margin = abs((ep * es) / leverage)

            if 'name' in order.info:
                if order.info['name'] == 'Entry':
                    print('{}: Entry Order Completed '.format(self.dt))
                    print('{}: Order Executed Price: {}, Executed Size {}'.format(self.dt,ep,es,))
                    print('{}: Position Value: {} Margin Used: {}'.format(self.dt,tv,self.margin))
                elif order.info['name'] == 'MCO':
                    print('{}: WARNING: Margin Close Out'.format(self.dt))
                else:
                    print('{}: Close Order Completed'.format(self.dt))

    def check_mco(self, value, margin_used):
        '''
        Controlla se il valore di chiusura del margine è sceso al di sotto della metà
        del margine utilizzato, chiudere la posizione.

        value: valore del portafoglio per uno specifico dato. Questo è essenzialmente
        uguale al valore di chiusura del margine che è saldo + pnl
        margin_used: margine iniziale
        '''

        if value < (margin_used /2):
            return True
        else:
            return False

class OandaCSVData(bt.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y-%m-%dT%H:%M:%S.%fZ'),
        ('datetime', 6),
        ('time', -1),
        ('open', 5),
        ('high', 3),
        ('low', 4),
        ('close', 1),
        ('volume', 7),
        ('openinterest', -1),
    )

tframes = dict(
    minutes=bt.TimeFrame.Minutes,
    daily=bt.TimeFrame.Days,
    weekly=bt.TimeFrame.Weeks,
    monthly=bt.TimeFrame.Months)

# Capitale iniziale
startcash = 10000

# Creo un istanza di cerebro
cerebro = bt.Cerebro()

# Imposto commissioni
cerebro.broker.setcommission(leverage=50)

# Aggiungo la strategia
cerebro.addstrategy(Mltests)

# Dati di Oanda
data = OandaCSVData(
    dataname='data/EUR_USD-2005-2017-D1.csv',
    fromdate=datetime(2005,1,1),
    todate=datetime(2006,1,1))

# Aggiungo i dati a Cerebro
cerebro.adddata(data)

# Imposto il capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')