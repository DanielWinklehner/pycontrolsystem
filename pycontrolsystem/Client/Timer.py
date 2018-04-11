import time
import datetime as dt
import operator

import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Timer(QObject):

    _sig_start = pyqtSignal(str)
    _sig_stop = pyqtSignal(str, float)

    def __init__(self, start_channel, start_val, start_comp, 
                       stop_channel, stop_val, stop_comp, 
                       mintime, continuous):

        super().__init__()
        self._start_channel = start_channel
        self._start_value = start_val
        self._start_comp = start_comp
        self._stop_channel = stop_channel
        self._stop_value = stop_val
        self._stop_comp = stop_comp
        self._min_time = mintime
        self._continuous = continuous
        self._dt = 0.05
        self._terminate = False
        self._timefmt = '%Y-%m-%d %H:%M:%S'

    @pyqtSlot()
    def run(self):
        self._terminate = False
        started = False
        starttime = None
        stoptime = None

        while not self._terminate:
            if not started:
                value = self._start_channel.value
                if self._start_comp(value, self._start_value):
                    started = True
                    starttime = dt.datetime.now()
                    self._sig_start.emit(starttime.strftime(self._timefmt))
            else:
                value = self._stop_channel.value
                if self._stop_comp(value, self._stop_value):
                    temptime = dt.datetime.now()
                    if (temptime - starttime).total_seconds() > self._min_time:
                        stoptime = temptime
                        if not self._continuous:
                            self._terminate = True
                        else:
                            started = False
                        self._sig_stop.emit(stoptime.strftime(self._timefmt), (stoptime - starttime).total_seconds())

            time.sleep(self._dt)

    @pyqtSlot()
    def terminate(self):
        self._terminate = True

    @property
    def start_signal(self):
        return self._sig_start

    @property
    def stop_signal(self):
        return self._sig_stop

    @property
    def start_channel(self):
        return self._start_channel

    @start_channel.setter
    def start_channel(self, val):
        self._start_channel = val

    @property
    def stop_channel(self):
        return self._stop_channel

    @stop_channel.setter
    def stop_channel(self, ch):
        self._stop_channel = ch

    @property
    def start_value(self):
        return self._start_value

    @start_value.setter
    def start_value(self, val):
        self._start_value = val

    @property
    def stop_value(self):
        return self._stop_value

    @stop_value.setter
    def stop_value(self, val):
        self._stop_value = val

    @property
    def start_comp(self):
        return self._start_comp

    @start_comp.setter
    def start_comp(self, val):
        self._start_comp = val

    @property
    def stop_comp(self):
        return self._stop_comp

    @stop_comp.setter
    def stop_comp(self, val):
        self._stop_comp = val

    @property
    def min_time(self):
        return self._min_time

    @min_time.setter
    def min_time(self, val):
        self._min_time = val

    @property
    def continuous(self):
        return self._continuous

    @continuous.setter
    def continuous(self, val):
        self._continuous = val

    @property
    def start_comp_str(self):
        if self._start_comp == operator.lt:
            return 'less'
        else:
            return 'greater'

    @property
    def stop_comp_str(self):
        if self._stop_comp == operator.lt:
            return 'less'
        else:
            return 'greater'
