#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Dialog for selecting which channels to plot

import datetime

from PyQt5.QtWidgets import QDialog, QColorDialog
from PyQt5.QtGui import QColor
from .ui_PlotSettingsDialog import Ui_PlotSettingsDialog

from lib.Channel import Channel

import pyqtgraph as pg

class PlotSettingsDialog(QDialog):

    def __init__(self, channel):
        super().__init__()
        self.ui = Ui_PlotSettingsDialog()
        self.ui.setupUi(self)
        self.ui.btnDone.clicked.connect(self.on_done_click)
        self.ui.rbXAuto.toggled.connect(self.on_x_auto_toggle)
        self.ui.rbYAuto.toggled.connect(self.on_y_auto_toggle)
        self.ui.btnColor.clicked.connect(self.on_color_click)

        self._channel = channel
        self._plot_settings = self._channel.plot_settings
        self.setup_form()

    def setup_form(self):
        xsettings = self._plot_settings['x']
        ysettings = self._plot_settings['y']
        wsettings = self._plot_settings['widget']

        # fill in limit text boxes
        self.ui.txtXMin.setText(datetime.datetime.fromtimestamp(xsettings['min']).strftime('%H:%M:%S'))
        self.ui.txtXMax.setText(datetime.datetime.fromtimestamp(xsettings['max']).strftime('%H:%M:%S'))
        self.ui.txtYMin.setText(str(ysettings['min']))
        self.ui.txtYMax.setText(str(ysettings['max']))
    
        # radio buttons for auto/manual mode
        if xsettings['mode'] == 'auto':
            self.ui.txtXMin.setEnabled(False)
            self.ui.txtXMax.setEnabled(False)
            self.ui.rbXAuto.toggle()
        else:
            self.ui.rbXManual.toggle()

        if ysettings['mode'] == 'auto':
            self.ui.txtYMin.setEnabled(False)
            self.ui.txtYMax.setEnabled(False)
            self.ui.rbYAuto.toggle()
        else:
            self.ui.rbYManual.toggle()

        # log scaling
        if xsettings['log']:
            self.ui.chkXLog.toggle()

        if ysettings['log']:
            self.ui.chkYLog.toggle()

        if xsettings['grid']:
            self.ui.chkXGrid.toggle()

        if ysettings['grid']:
            self.ui.chkYGrid.toggle()

        # color
        self.ui.lblColor.setStyleSheet('padding: 0 10; background-color: {}'.format(wsettings['color']))
    def on_x_auto_toggle(self, chkstate):
        if chkstate:
            self.ui.txtXMin.setEnabled(False)
            self.ui.txtXMax.setEnabled(False)
        else:
            self.ui.txtXMin.setEnabled(True)
            self.ui.txtXMax.setEnabled(True)

    def on_y_auto_toggle(self, chkstate):
        if chkstate:
            self.ui.txtYMin.setEnabled(False)
            self.ui.txtYMax.setEnabled(False)
        else:
            self.ui.txtYMin.setEnabled(True)
            self.ui.txtYMax.setEnabled(True)

    def on_color_click(self):
        init_color = QColor(self._plot_settings['widget']['color'])
        _colordialog = QColorDialog(init_color)
        _colordialog.exec_()
        x = _colordialog.currentColor().name()
        self._plot_settings['widget']['color'] = x
        self.ui.lblColor.setStyleSheet('padding: 0 10; background-color: {}'.format(x))

    def on_done_click(self):
        # Log scaling
        if self.ui.chkXLog.isChecked():
            self._plot_settings['x']['log'] = True
        else:
            self._plot_settings['x']['log'] = False

        if self.ui.chkYLog.isChecked():
            self._plot_settings['y']['log'] = True
        else:
            self._plot_settings['y']['log'] = False

        if self.ui.chkXGrid.isChecked():
            self._plot_settings['x']['grid'] = True
        else:
            self._plot_settings['x']['grid'] = False

        if self.ui.chkYGrid.isChecked():
            self._plot_settings['y']['grid'] = True
        else:
            self._plot_settings['y']['grid'] = False

        # plot limits
        if not self.ui.rbXAuto.isChecked():
            #try:
                minim = datetime.datetime.strptime(self.ui.txtXMin.text(), '%H:%M:%S')
                maxim = datetime.datetime.strptime(self.ui.txtXMax.text(), '%H:%M:%S')
                
                d = datetime.datetime.today().date().day
                m = datetime.datetime.today().date().month
                y = datetime.datetime.today().date().year

                minim = minim.replace(year=y, month=m, day=d)
                maxim = maxim.replace(year=y, month=m, day=d)

                if minim < maxim:
                    self._plot_settings['x']['min'] = minim.timestamp() 
                    self._plot_settings['x']['max'] = maxim.timestamp()
                    self._plot_settings['x']['mode'] = 'manual'
                else:
                    print('bad values for limits')
                    return
            #except:
            #    print('bad values for limits')
            #    return
        else:
            self._plot_settings['x']['mode'] = 'auto'

        if not self.ui.rbYAuto.isChecked():
            try:
                minim = float(self.ui.txtYMin.text())
                maxim = float(self.ui.txtYMax.text())
                
                if minim < maxim:
                    self._plot_settings['y']['min'] = minim 
                    self._plot_settings['y']['max'] = maxim
                    self._plot_settings['y']['mode'] = 'manual'
                else:
                    print('bad values for limits')
                    return
            except:
                print('bad values for limits')
                return
        else:
            self._plot_settings['y']['mode'] = 'auto'

        self._channel.plot_settings = self._plot_settings
        self.accept()
