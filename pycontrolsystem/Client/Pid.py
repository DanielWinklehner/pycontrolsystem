import time

import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class Pid(QObject):
    _sig_set_value = pyqtSignal(float)
    _sig_skip_value = pyqtSignal(float)
    _sig_ma_total = pyqtSignal(float)

    def __init__(self, channel, target=0.0, coeffs=[1.0, 1.0, 1.0], dt=0.5,
                 ma=1, warmup=0, offset=0.0, ):
        super().__init__()
        self._target = target
        self._channel = channel
        self._coeffs = coeffs
        self._dt = dt
        self._ma = ma
        self._warmup = warmup
        self._offset = offset

    @pyqtSlot()
    def run(self):
        self._terminate = False
        self._pause = False
        prev_err = 0.
        integral = 0.
        ma_count = 0
        warmup_count = 0
        ma_sum_values = 0.0
        while not self._terminate:

            if self._pause:
                time.sleep(self._dt)
                continue

            if ma_count < self._ma:
                ma_count += 1
                ma_sum_values += self._channel.value

            if ma_count < self._ma:
                self._sig_ma_total.emit(ma_sum_values / ma_count)
            else:
                avg = ma_sum_values / self._ma
                err = self._target - avg
                integral += err * self._dt * self._ma
                deriv = (err - prev_err) / (self._dt * self._ma)

                resp = sum(np.multiply([err, integral, deriv], self._coeffs)) + self._offset

                ma_count = 0
                ma_sum_values = 0.0

                if warmup_count < self._warmup:
                    warmup_count += 1
                    self._sig_skip_value.emit(resp)
                else:
                    self._sig_set_value.emit(resp)
                prev_err = err

            time.sleep(self._dt)

    @pyqtSlot()
    def terminate(self):
        self._terminate = True

    @pyqtSlot()
    def pause(self):
        self._pause = True

    @pyqtSlot()
    def unpause(self):
        self._pause = False

    @property
    def set_signal(self):
        return self._sig_set_value

    @property
    def skip_signal(self):
        return self._sig_skip_value

    @property
    def ma_signal(self):
        return self._sig_ma_total

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, ch):
        self._channel = ch

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, val):
        self._target = val

    @property
    def coeffs(self):
        return self._coeffs

    @property
    def dt(self):
        return self._dt

    @property
    def ma(self):
        return self._ma

    @ma.setter
    def ma(self, value):
        if value < 1:
            print('bad value for ma')
            return

        self._ma = value

    @property
    def warmup(self):
        return self._warmup

    @property
    def offset(self):
        return self._offset
