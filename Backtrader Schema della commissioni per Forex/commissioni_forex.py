import backtrader as bt
from datetime import datetime

class forexSpreadCommisionScheme(bt.CommInfoBase):
    '''
    Questo schema di commissioni tenta di calcolare la commissione nascosta
    nello spread dalla maggior parte dei broker forex.
    Presuppone che vengano utilizzati i dati del punto medio tra bid e ask.

    *Nuovi parametri*
    spread: Float, lo spread in pips dello strumento
    JPY_pair: Bool, indica se la coppia scambiata è una coppia JPY
    acc_counter_currency: Bool, indica se la valuta del conto è la stessa della
    valuta del contatore. Se falso, si presume che sia la valuta di base
    '''
    params = (
        ('spread', 2.0),
        ('stocklike', False),
        ('JPY_pair', False),
        ('acc_counter_currency', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
    )

    def _getcommission(self, size, price, pseudoexec):
        '''
        Questo schema applicherà metà della commissione all'acquisto e metà alla vendita.
        Per le coppie JPY il moltiplicatore viene modificato di conseguenza.
        Se la valuta del conto è la stessa della valuta di base, modificare il calcolo del valore in pip.
        '''
        if self.p.JPY_pair == True:
            multiplier = 0.01
        else:
            multiplier = 0.0001

        if self.p.acc_counter_currency == True:
            comm = abs((self.p.spread * (size * multiplier) / 2))
        else:
            comm = abs((self.p.spread * ((size / price) * multiplier) / 2))

        return comm


class testStrategy(bt.Strategy):
    '''
    Strategia super semplice per verificare se lo schema delle commissioni viene applicato correttamente
    '''

    def __init__(self):
        self.count = 0

    def next(self):
        self.count = len(self)
        if self.count == 1:
            self.buy(size=10000)
        elif self.count == 10:
            self.close()
        else:
            pass

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        print(('OPERATION PROFIT, GROSS {}, NET {}'.format(trade.pnl, trade.pnlcomm)))


if __name__ == '__main__':

    # Variabile per il capitale iniziale
    startcash = 100000

    # Creare un'istanza di cerebro
    cerebro = bt.Cerebro()

    #Aggiungere lo schema commissionale
    comminfo = forexSpreadCommisionScheme(spread=10)
    cerebro.broker.addcommissioninfo(comminfo)

    # Download dei dati di Apple da Yahoo Finance.
    data = bt.feeds.YahooFinanceData(
        dataname='EURUSD=X',
        fromdate=datetime(2020, 6, 1),
        todate=datetime(2022, 1, 1),
        buffered=True
    )

    # Aggiungere i dati di Apple a Cerebro
    cerebro.adddata(data)

    cerebro.addstrategy(testStrategy)
    # Impostare il capitale iniziale
    cerebro.broker.setcash(startcash)

    # Esecuzione
    cerebro.run()
