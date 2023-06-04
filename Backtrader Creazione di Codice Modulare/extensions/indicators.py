import backtrader as bt

class SwingInd(bt.Indicator):
    '''
    Un semplice indicatore di swing che misura le oscillazioni (il valore più basso/più alto)
    in un determinato periodo di tempo.
    '''
    lines = ('swings', 'signal')
    params = (('period', 7),)

    def __init__(self):
        # Imposta l'intervallo dello swing: il numero di barre prima e dopo lo swing
        # necessarie per identificare uno swing
        self.swing_range = (self.p.period * 2) + 1
        self.addminperiod(self.swing_range)

    def next(self):
        # Calcolo gli highs/lows nel periodo
        highs = self.data.high.get(size=self.swing_range)
        lows = self.data.low.get(size=self.swing_range)
        # Controllo se la barra nel centro del ragne è più grande delle alte
        if highs.pop(self.p.period) > max(highs):
            self.lines.swings[-self.p.period] = 1  # aggiunge un nuovo swing
            self.lines.signal[0] = 1  # crea il segnale
        elif lows.pop(self.p.period) < min(lows):
            self.lines.swings[-self.p.period] = -1  # aggiunge un nuovo swing
            self.lines.signal[0] = -1  # crea il segnale
        else:
            self.lines.swings[-self.p.period] = 0
            self.lines.signal[0] = 0