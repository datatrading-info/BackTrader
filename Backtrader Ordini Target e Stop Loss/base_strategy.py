
import backtrader as bt
from datetime import datetime

class TestStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        date = self.data.datetime.date()
        long_stop = self.data.close[0] - 50 # Non sarà colpito
        short_stop = self.data.close[0] + 50 # Non sarà colpito
        if not self.position:
            if date == datetime(2018,1,11).date():
                # Il prezzo chiude a $100 e successivamente apre a $100
                # test base senza gap
                buy_ord = self.buy()
                buy_ord.addinfo(name="Long Market Entry")
                self.sl_ord = self.sell(exectype=bt.Order.Stop, price=long_stop)
                self.sl_ord.addinfo(name='Long Stop Loss')
            elif date == datetime(2018,12,27).date():
                # Il prezzo chiude a $100 e successivamente apre a $150
                # Inizio del test di inversione della prima posizione
                # Ancora flat al momento
                buy_ord = self.buy()
                buy_ord.addinfo(name="Long Market Entry")
                self.sl_ord = self.sell(exectype=bt.Order.Stop, price=long_stop)
                self.sl_ord.addinfo(name='Long Stop Loss')
        else:
            # NOTA oco=self.sl_ord è necessatio per canellare gli stop loss già a mercato
            if date == datetime(2018,1,25).date():
                # Il prezzo chiude a $140 e successivamente apre a $140
                # Primo test di chiusura posizione - profitto di $40
                cls_ord = self.close(oco=self.sl_ord)
                cls_ord.addinfo(name="Close Market Order")
            elif date == datetime(2019,1,1).date():
                # Il prezzo chiude a $190 e successivamente apre a $190
                # Prima posizione da invertire
                # Vendiamo da una posizione long con la dimensione desiderata
                # Adesso abbiamo una posizione short.
                sell_ord = self.sell(oco=self.sl_ord)
                sell_ord.addinfo(name="Short Market Entry")
                self.sl_ord = self.buy(exectype=bt.Order.Stop, price=short_stop)
                self.sl_ord.addinfo(name='Short Stop Loss')
            elif date == datetime(2019,1,6).date():
                # Abbiamo una posizione short
                # Il prezzo chiude a $190 e successivamente apre a $190
                # NOTA oco=self.sl_ord è necessatio per canellare gli stop loss già a mercato
                # Acquistiamo per invertire effettivamente una vendita
                buy_ord = self.buy(oco=self.sl_ord)
                buy_ord.addinfo(name="Long Market Entry")
                self.sl_ord = self.sell(exectype=bt.Order.Stop, price=long_stop)
                self.sl_ord.addinfo(name='Long Stop Loss')
            elif date == datetime(2019,1,11).date():
                # Il prezzo chiude a $190 e apre a $190 nella candela successiva
                # Chiudere alla fine
                cls_ord = self.close(oco=self.sl_ord)
                cls_ord.addinfo(name="Close Market Order")

    def notify_order(self, order):
        date = self.data.datetime.datetime().date()

        if order.status == order.Accepted:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('{} Order Accepted'.format(order.info['name']))
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))


        if order.status == order.Completed:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('{} Order Completed'.format(order.info['name']))
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
            print('Created: {} Price: {} Size: {}'.format(bt.num2date(order.created.dt), order.created.price,order.created.size))
            print('-'*80)

        if order.status == order.Canceled:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('{} Order Canceled'.format(order.info['name']))
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))

        if order.status == order.Rejected:
            print('-'*32,' NOTIFY ORDER ','-'*32)
            print('WARNING! {} Order Rejected'.format(order.info['name']))
            print('{}, Status {}: Ref: {}, Size: {}, Price: {}'.format(
                                                        date,
                                                        order.status,
                                                        order.ref,
                                                        order.size,
                                                        'NA' if not order.price else round(order.price,5)
                                                        ))
            print('-'*80)

    def notify_trade(self, trade):
        date = self.data.datetime.datetime()
        if trade.isclosed:
            print('-'*32,' NOTIFY TRADE ','-'*32)
            print('{}, Close Price: {}, Profit, Gross {}, Net {}'.format(
                                                date,
                                                trade.price,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))
            print('-'*80)

startcash = 10000

# Creare un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(TestStrategy)

# Creare un Data Feed
data = bt.feeds.GenericCSVData(
    timeframe=bt.TimeFrame.Days,
    compression=1,
    dataname='data/TestData.csv',
    nullvalue=0.0,
    dtformat=('%m/%d/%Y'),
    datetime=0,
    time=-1,
    high=2,
    low=3,
    open=1,
    close=4,
    volume=-1,
    openinterest=-1 #-1 significa non usata
    )

# Aggiungere i dati
cerebro.adddata(data)

# Impostare il capitale iniziale
cerebro.broker.setcash(startcash)

# Esecuzione del backtest
cerebro.run()

# Ottenre il valore finale del portafoglio
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

# Stampa dei risultati finali
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

# Grafico dei risultati
cerebro.plot(style='candlestick')