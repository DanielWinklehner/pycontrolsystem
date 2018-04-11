#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Custom dial class for setting channel values

from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QDial, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class ChannelDial(QWidget):

    valueChanged = pyqtSignal(object)

    def __init__(self, channel):
        super().__init__()

        self._channel = channel

        self._dial = NoMouseDial()
        self._dial.valueChanged.connect(self.on_dial_value_changed)

        self._txtWrite = QLineEdit()
        self._txtWrite.returnPressed.connect(self.on_text_return_pressed)

        self._lblUnit = QLabel(self._channel.unit)

        hbox = QHBoxLayout()
        self.setLayout(hbox)
        hbox.addWidget(self._dial)
        hbox.addWidget(self._txtWrite)
        hbox.addWidget(self._lblUnit)

    # Function aliases for dial
    def setMaximum(self, val):
        self._dial.setMaximum(val)

    def value(self):
        return self._dial.value()

    def maximum(self):
        return self._dial.maximum()

    def update(self):
        self._lblUnit.setText(self._channel.unit)

    @pyqtSlot()
    def on_text_return_pressed(self):
        try:
            val = self._channel.data_type(self._txtWrite.text())
        except:
            print('bad value entered')
            return

        if val > self._channel.upper_limit or val < self._channel.lower_limit:
            print('bad value entered')
            return

        # this indirectly calls on_dial_value_changed, which sends the signal and formats the text box
        self._dial.setValue(
                (val - self._channel.lower_limit) / (self._channel.upper_limit - self._channel.lower_limit) * self.maximum())
        #self._dial.setValue( (val / self._channel.upper_limit) * self.maximum())

    @pyqtSlot(int)
    def on_dial_value_changed(self, val):
        self.valueChanged.emit(val)
        dispval = self._channel.lower_limit + (self._channel.upper_limit - self._channel.lower_limit) * val / self.maximum()
        self._txtWrite.setText('{1:.{0}{2}}'.format(self._channel.precision, dispval, self._channel.display_mode))

    @property
    def dial(self):
        return self._dial

class NoMouseDial(QDial):
    def __init__(self):
        super().__init__()

    # dial should be scroll wheel only, override all mouse events
    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

