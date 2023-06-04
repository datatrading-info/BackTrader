import backtrader as bt
from backtrader import Analyzer
from backtrader.utils import AutoOrderedDict
from backtrader.indicators import PivotPoint

class pivotPointAnalyzer(Analyzer):
    '''
    Analyzer per restituire alcune statistiche di base che mostrano:
        - Totale giorni/periodi analizzati
        - La percentuale con cui p è stata toccata
        - La percentuale con cui s1 è stata toccata
        - La percentuale con cui s2 è stata toccata
        - La percentuale con cui r1 è stata toccata
        - La percentuale con cui r2 è stata toccata
        - Le percentuali con cui s1 e r1 sono state toccate nello stesso giorno/periodo
        - Le percentuali con cui s1 e r2 sono state toccate nello stesso giorno/periodo
        - La percentuale con cui s2 e r1 sono state toccate nello stesso giorno/periodo
        - La percentuale con cui s2 e r1 sono state toccate nello stesso giorno/periodo
        - La percentuale con cui p è stata toccata senza toccare s1
        - La percentuale con cui p è stata toccata senza toccare r1
        - La percentuale con cui s1 è stata toccata senza toccare r1
        - La percentuale con cui r1 è stata toccata senza toccare s1
    '''

    def __init__(self):
        #data1 è il resample di data
        self.pivots = PivotPoint()
        # Non vogliamo stampare l'analyzer
        self.pivots.autoplot = False


    def create_analysis(self):
        hit_desc = ('Mesures the frequency in percent that each pivot\n      '
            'was hit over the course of the time period analyzed\n')

        db_desc = ('Mesures the frequency in percent that a pair of pivots\n      '
            'were hit on the same day over the course of the time period analyzed\n')

        xy_desc = ('Mesures the frequency in percent that one pivot (x)\n      '
            'was hit without hitting another pivot (y) on the same day\n      '
            'over the course of the time period analyzed\n')

        self.rets = AutoOrderedDict()
        self.counts = AutoOrderedDict()
        self.counts.total = 0

        self.counts['Hit']['R1'] = 0
        self.counts['Hit']['R2'] = 0
        self.counts['Hit']['P'] = 0
        self.counts['Hit']['S1'] = 0
        self.counts['Hit']['S2'] = 0

        self.counts['DB']['S1 & R1'] = 0
        self.counts['DB']['S1 & R2'] = 0
        self.counts['DB']['S2 & R1'] = 0
        self.counts['DB']['S2 & R2'] = 0

        self.counts['XY']['x=P y=R2'] = 0
        self.counts['XY']['x=P y=R1'] = 0
        self.counts['XY']['x=P y=S2'] = 0
        self.counts['XY']['x=P y=S1'] = 0
        self.counts['XY']['x=R1 y=S2'] = 0
        self.counts['XY']['x=R1 y=S1'] = 0
        self.counts['XY']['x=R1 y=P'] = 0
        self.counts['XY']['x=R2 y=S2'] = 0
        self.counts['XY']['x=R2 y=S1'] = 0
        self.counts['XY']['x=R2 y=P'] = 0
        self.counts['XY']['x=S1 y=R2'] = 0
        self.counts['XY']['x=S1 y=R1'] = 0
        self.counts['XY']['x=S1 y=P'] = 0
        self.counts['XY']['x=S2 y=R2'] = 0
        self.counts['XY']['x=S2 y=R1'] = 0
        self.counts['XY']['x=S2 y=P'] = 0

        self.rets['Hit']['Description'] = hit_desc
        self.rets['Hit']['R1'] = 0
        self.rets['Hit']['R2'] = 0
        self.rets['Hit']['P'] = 0
        self.rets['Hit']['S1'] = 0
        self.rets['Hit']['S2'] = 0

        self.rets['DB']['Description'] = db_desc
        self.rets['DB']['S1 & R1'] = 0
        self.rets['DB']['S1 & R2'] = 0
        self.rets['DB']['S2 & R1'] = 0
        self.rets['DB']['S2 & R2'] = 0

        self.rets['XY']['Description'] = xy_desc
        self.rets['XY']['x=P y=R2'] = 0
        self.rets['XY']['x=P y=R1'] = 0
        self.rets['XY']['x=P y=S2'] = 0
        self.rets['XY']['x=P y=S1'] = 0
        self.rets['XY']['x=R1 y=S2'] = 0
        self.rets['XY']['x=R1 y=S1'] = 0
        self.rets['XY']['x=R1 y=P'] = 0
        self.rets['XY']['x=R2 y=S2'] = 0
        self.rets['XY']['x=R2 y=S1'] = 0
        self.rets['XY']['x=R2 y=P'] = 0
        self.rets['XY']['x=S1 y=R2'] = 0
        self.rets['XY']['x=S1 y=R1'] = 0
        self.rets['XY']['x=S1 y=P'] = 0
        self.rets['XY']['x=S2 y=R2'] = 0
        self.rets['XY']['x=S2 y=R1'] = 0
        self.rets['XY']['x=S2 y=P'] = 0

    def next(self):
        r2 = self.pivots.lines.r2[-1]
        r1 = self.pivots.lines.r1[-1]
        p = self.pivots.lines.p[-1]
        s1 = self.pivots.lines.s1[-1]
        s2 = self.pivots.lines.s2[-1]

        o = self.data.open[0]
        h = self.data.high[0]
        l = self.data.low[0]
        c = self.data.close[0]

        pivots = [
            ['R2', r2],
            ['R1', r1],
            ['P', p],
            ['S1', s1],
            ['S2', s2]]

        for piv in pivots:
            #if piv[0] == 'r2':
                #print('h: {} L {}, piv {}'.format(h,l, piv[1]))
            if h > piv[1] and l < piv[1]:
                #print('h: {} L {}, piv {}'.format(h,l, piv[1]))
                # Pivot ttoccato
                self.counts['Hit'][piv[0]] +=1

        db_pivots = [
            ['S1 & R1', s1, r1],
            ['S1 & R2', s1, r2],
            ['S2 & R1', s2, r1],
            ['S2 & R2', s2, r2]
        ]
        # DB
        for piv in db_pivots:
            db_conditions = [
                h > piv[1],
                h > piv[2],
                l < piv[1],
                l < piv[2],
            ]
            if all(db_conditions):
                self.counts['DB'][piv[0]] +=1

        # X senza toccare Y
        xy_pivots = [
        ['x=P y=R2', p, r2, 'r'],
        ['x=P y=R1', p, r1, 'r'],
        ['x=P y=S2', p, s2, 's'],
        ['x=P y=S1', p, s1,'s'],
        ['x=R1 y=S2', r1, s2, 's'],
        ['x=R1 y=S1', r1, s1, 's'],
        ['x=R1 y=P', r1, p, 'p'],
        ['x=R2 y=S2', r2, s2, 's'],
        ['x=R2 y=S1', r2, s1, 's'],
        ['x=R2 y=P', r2, p, 'p'],
        ['x=S1 y=R2', s1, r2, 'r'],
        ['x=S1 y=R1', s1, r1, 'r'],
        ['x=S1 y=P', s1, p, 'p'],
        ['x=S2 y=R2', s2, r2, 'r'],
        ['x=S2 y=R1', s2, r1, 'r'],
        ['x=S2 y=P', s2, p, 'p']
        ]
        for piv in xy_pivots:
            if piv[3] == 'r':
                db_conditions = [
                h > piv[1],
                l < piv[1],
                h < piv[2]
                ]
            elif piv[3] == 's':
                db_conditions = [
                h > piv[1],
                l < piv[1],
                l > piv[2]
                ]
            elif piv[3] == 'p':
                db_conditions = [
                h > piv[1],
                l < piv[1],
                (h > piv[2] and l > piv[2]) or (h < piv[2] and l < piv[2])
                ]

            if all(db_conditions):
                self.counts['XY'][piv[0]] +=1


    def stop(self):
        self.counts.total = len(self.data)
        # ITERARE SU COUNTS COSI' LA DESCRIZIONE NON CAUSA ERRORI
        for key, value in self.counts['Hit'].items():
            try:
                perc = round((value / self.counts.total) * 100,2)
                self.rets['Hit'][key] = str(perc) + '%'
            except ZeroDivisionError:
                self.rets['Hit'][key] = '0%'

        # ITERARE SU COUNTS COSI' LA DESCRIZIONE NON CAUSA ERRORI
        for key, value in self.counts['DB'].items():
            try:
                perc = round((value / self.counts.total) * 100,2)
                self.rets['DB'][key] = str(perc) + '%'
            except ZeroDivisionError:
                self.rets['DB'][key] = '0%'

        # ITERARE SU COUNTS COSI' LA DESCRIZIONE NON CAUSA ERRORI
        for key, value in self.counts['XY'].items():
            try:

                perc = round((value / self.counts.total) * 100,2)
                self.rets['XY'][key] = str(perc) + '%'
            except ZeroDivisionError:
                self.rets['XY'][key] = '0%'

        self.rets._close()