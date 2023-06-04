import backtrader as bt
import datetime
import time


class TrendLine(bt.Indicator):
    lines = ('signal', 'trend')
    params = (
        ('x1', None),
        ('y1', None),
        ('x2', None),
        ('y2', None)
    )

    def __init__(self):
        self.p.x1 = datetime.datetime.strptime(self.p.x1, "%Y-%m-%d %H:%M:%S")
        self.p.x2 = datetime.datetime.strptime(self.p.x2, "%Y-%m-%d %H:%M:%S")
        x1_time_stamp = time.mktime(self.p.x1.timetuple())
        x2_time_stamp = time.mktime(self.p.x2.timetuple())
        self.m = self.get_slope(x1_time_stamp, x2_time_stamp, self.p.y1, self.p.y2)
        self.B = self.get_y_intercept(self.m, x1_time_stamp, self.p.y1)
        self.plotlines.trend._plotskip = True

    def next(self):
        date = self.data0.datetime.datetime()
        date_timestamp = time.mktime(date.timetuple())
        Y = self.get_y(date_timestamp)
        self.lines.trend[0] = Y

        # Controlla se il prezzo a superato al rialzo o ribasso.
        if (self.data0.high[-1] < Y) and (self.data0.high[0] > Y):
            self.lines.signal[0] = -1
            return

        # Controlla per i cross al ribasso (support)
        elif (self.data0.low[-1] > Y) and (self.data0.low[0] < Y):
            self.lines.signal[0] = 1
            return

        else:
            self.lines.signal[0] = 0

    def get_slope(self, x1, x2, y1, y2):
        m = (y2 - y1) / (x2 - x1)
        return m

    def get_y_intercept(self, m, x1, y1):
        b = y1 - m * x1
        return b

    def get_y(self, ts):
        Y = self.m * ts + self.B
        return Y

