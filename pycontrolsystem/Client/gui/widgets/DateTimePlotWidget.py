#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Custom pyqtgraph PlotWidget class with a timestamp axis

import datetime as dt
import time
import pyqtgraph as pg


class DateTimeAxis(pg.AxisItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        strings = []
        # Fix for initialization (which are usually just the floats 0.0, 1.0)
        # if values == [0.0, 1.0]:
        #     values = [time.time(), time.time()]
        for v in values:
            try:
                val = dt.datetime.fromtimestamp(v).strftime('%H:%M:%S')
            except OSError:
                val = str(v)
            strings.append(val)
        return strings


class DateTimePlotWidget(pg.PlotWidget):
    """ Plot Widget with date time axis, and ability to copy settings """

    def __init__(self, *args, **kwargs):
        # Give the settings parameter from kwargs a default value
        settings = kwargs.pop('settings', None)

        # Initialize this widget with the DateTimeAxis by appending it to the kwargs
        self._dateaxis = DateTimeAxis(orientation='bottom')
        nkwargs = kwargs
        nkwargs['axisItems'] = {'bottom': self._dateaxis}
        super().__init__(*args, **nkwargs)

        # self.getAxis('left').textWidth = 40
        # self.getAxis('left').setWidth(40)

        self._settings = settings
        self._curve = self.plot()
        self.update_settings()

    @property
    def curve(self):
        return self._curve

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, newsettings):
        self._settings = newsettings
        self.update_settings()

    def update_settings(self):
        if self._settings is None:
            return

        autorangeaxes = ''
        if self._settings['x']['mode'] != 'auto':
            self.setXRange(self._settings['x']['min'],
                           self._settings['x']['max'],
                           padding=0.0)
        else:
            autorangeaxes += 'x'

        if self._settings['y']['mode'] != 'auto':
            self.setYRange(self._settings['y']['min'],
                           self._settings['y']['max'],
                           padding=0.0)
        else:
            autorangeaxes += 'y'

        if autorangeaxes != '':
            self.enableAutoRange(axis=autorangeaxes)

        self.setLogMode(x=self._settings['x']['log'],
                        y=self._settings['y']['log'])

        self.showGrid(x=self._settings['x']['grid'],
                      y=self._settings['y']['grid'])

        self._curve.setData(pen=self._settings['widget']['color'])
