import backtrader as bt
from datetime import datetime
from collections import OrderedDict

class RsiStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
            else:
                if self.rsi > 70:
                    self.sell(size=100)


def tradeAnalysis(analyzer):
    '''
    Funzione per stampare i risultati dell'Analisi Tecnica in un bel formato.
    '''
    # Ottenere i risultati che ci interessano
    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total,2)
    strike_rate = (total_won / total_closed) * 100
    # Definire le righe
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate','Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed,total_won,total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]
    # Controllore che il set degli headers è il più lungo
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)
    # Stampa le righe
    print_list = [h1,r1,h2,r2]
    row_format ="{:<15}" * (header_length + 1)
    print("Trade Analysis Results:")
    for row in print_list:
        print(row_format.format('',*row))

def SQN(analyzer):
    sqn = round(analyzer.sqn,2)
    print('SQN: {}'.format(sqn))

# Variabile per il capitale iniziale
startcash = 100000

# Creare un'istanza di cerebro
cerebro = bt.Cerebro()

# Aggiungere la strategia
cerebro.addstrategy(RsiStrategy)

# Download dei dati di Apple da Yahoo Finance.
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate = datetime(2009,1,1),
    todate = datetime(2017,1,1),
    buffered= True
    )

# Aggiungere i dati di Apple a Cerebro
cerebro.adddata(data)

# Impostare il capitale iniziale
cerebro.broker.setcash(startcash)

# Aggiungere gli analyzer
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

# Esecuzione
strategies = cerebro.run()
rsiStrat = strategies[0]

# Stampa degli analyzer
tradeAnalysis(rsiStrat.analyzers.ta.get_analysis())
SQN(rsiStrat.analyzers.sqn.get_analysis())

# Valore finale del portafoglio
portvalue = cerebro.broker.getvalue()

# Stampa del risultato finale
print('Final Portfolio Value: ${}'.format(portvalue))

# Grafico dei risultati finali
cerebro.plot(style='candlestick')