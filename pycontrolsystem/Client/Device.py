#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Device representation class

import json
import time
import threading

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
        QGroupBox, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from Channel import Channel
from gui.widgets.EntryForm import EntryForm

class DeviceWidget(QWidget):

    def __init__(self, device):
        super().__init__()

        self._device = device

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._gb = QGroupBox(self._device.label)

        self._layout.addWidget(self._gb)

        # label to display this device's polling rate
        self._polling_rate_label = QLabel('Polling rate: --')
        self._layout.addWidget(self._polling_rate_label)
        self._layout.addStretch()

        self._gblayout = QVBoxLayout()
        self._gb.setLayout(self._gblayout)

        self._hasMessage = False
        self._retry_time = self._device._retry_time

        self._retry_thread = None

    def show_error_message(self, message=''):
        if not self._hasMessage:

            self._messageframe = QFrame()
            vbox = QVBoxLayout()
            vbox.setContentsMargins(0, 0, 0, 0)
            self._messageframe.setLayout(vbox)

            self._txtmessage = QLabel()
            self._txtmessage.setWordWrap(True)
            vbox.addWidget(self._txtmessage)

            self._txtretry = QLabel('Retrying ...') #in {} seconds...'.format(self._retry_time))
            vbox.addWidget(self._txtretry)

            self._gb.setEnabled(False)
            self._layout.insertWidget(0, self._messageframe)

            self._hbox = QHBoxLayout()
            self._btnRetry = QPushButton('Force Retry')
            self._polling_rate_label.setText('Polling rate: --')
            self._btnRetry.clicked.connect(self.force_retry_connect)
            self._hbox.addStretch()
            self._hbox.addWidget(self._btnRetry)
            self._hbox.addStretch()
            self._layout.insertLayout(3, self._hbox)

            self._hasMessage = True

        self._txtmessage.setText('<font color="red">{}</font>'.format(message))

        if self._retry_thread is not None:
            # probably ok since the thread isn't doing anything critical
            del self._retry_thread

        #self._retry_thread = threading.Thread(target=self.test_update_retry_label, args=())
        #self._retry_thread.start()

    def force_retry_connect(self):
        self._device.unlock()

    '''
    def test_update_retry_label(self):
        for i in range(self._retry_time):
            self._txtretry.setText('Retrying in {} seconds...'.format(self._retry_time - i))
            time.sleep(1)
        self._device.unlock()
        self._txtretry.setText('Retrying')
    '''

    def set_retry_label(self, time):
        self._txtretry.setText('Retrying in {} seconds...'.format(str(time)))

    def hide_error_message(self):
        if self._hasMessage:
            wdg = self._layout.itemAt(0).widget()
            wdg.deleteLater()
            self._gb.setEnabled(True)
            self._hasMessage = False

            self._btnRetry.deleteLater()
            self._hbox.setParent(None)

    @property
    def gblayout(self):
        return self._gblayout

class Device(QObject):

    _sig_entry_form_ok = pyqtSignal(object, dict)
    _sig_delete = pyqtSignal(object)

    # emit when device changes need to be send to server (lock/unlock)
    _sig_update_server = pyqtSignal()

    def __init__(self, name='', device_id='', label='', channels=None,
                 driver='ArduinoMega', overview_order=-1):
        super().__init__()

        self._name = name
        self._label = label

        self._channels = {}  # This is a dictionary of channels with their names as keys.
        if channels is not None:
            self._channels = channels

        self._device_id = device_id
        self._driver = driver

        self._parent = None
        self._locked = False

        self._pages = ['overview']
        self._overview_order = overview_order

        self._error_message = ''
        self._retry_time = 30
        self._polling_rate = 0. # Hz

        self._entry_form = EntryForm(self._label, '', self.user_edit_properties(), self)
        self._entry_form.sig_save.connect(self.save_changes)
        self._entry_form.sig_delete.connect(self.delete)

        self._initialized = False

    @property
    def initialized(self):
        return self._initialized

    def initialize(self):

        # create gui representation
        self._overview_widget = DeviceWidget(self)
        self._gblayout = self._overview_widget.gblayout
        self._polling_rate_label = self._overview_widget._polling_rate_label

        self._initialized = True
        self._entry_form.add_delete_button()

    def reset_entry_form(self):
        self._entry_form.properties = self.user_edit_properties()
        self._entry_form.reset()

    @pyqtSlot(dict)
    def save_changes(self, newvals):
        """ Validates the user data entered into the device's entry form """
        validvals = {}
        for prop_name, val in newvals.items():
            if prop_name == 'overview_order':
                try:
                    value = int(val)
                except:
                    print('Display order must be an int')
                    return
            else:
                if val != '':
                    value = val
                else:
                    print('No value entered for {}.'.format(
                        self.user_edit_properties()[prop_name]['display_name']))
                    return

            validvals[prop_name] = value

        self._sig_entry_form_ok.emit(self, validvals)

    @pyqtSlot()
    def delete(self):
        self._sig_delete.emit(self)

    @property
    def sig_entry_form_ok(self):
        return self._sig_entry_form_ok

    @property
    def sig_delete(self):
        return self._sig_delete

    @property
    def sig_update_server(self):
        return self._sig_update_server

    @property
    def overview_widget(self):
        return self._overview_widget

    @staticmethod
    def driver_list():
        return ['ArduinoMega', 'ArduinoMicro', 'RS485', 'FT232R', 'Teensy', 'Prolific', 'MATSUSADA']

    def user_edit_properties(self):
        """ Returns list of properties that should be user-editable
            key name must match a property of this class """

        return {
                'name': {
                    'display_name': 'Name',
                    'entry_type': 'text',
                    'value': self._name,
                    'display_order': 1
                    },
                'device_id': {
                    'display_name': 'Device ID',
                    'entry_type': 'text',
                    'value': self._device_id,
                    'display_order': 2
                    },
                'label': {
                    'display_name': 'Label',
                    'entry_type': 'text',
                    'value': self._label,
                    'display_order': 3
                    },
                'driver': {
                    'display_name': 'Driver',
                    'entry_type': 'combo',
                    'value': self._driver,
                    'defaults': self.driver_list(),
                    'display_order': 4
                    },
                'overview_order': {
                    'display_name': 'Display Order',
                    'entry_type': 'text',
                    'value': self._overview_order,
                    'display_order': 5
                    },
                }

    @property
    def entry_form(self):
        return self._entry_form.widget

    def update(self):
        # reorder the channels
        if not self._initialized:
            return

        while self._gblayout.count():
            child = self._gblayout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        chlist = [ch for chname, ch in reversed(sorted(self._channels.items(),
                                                        key=lambda x: x[1].display_order))]

        for idx, ch in enumerate(chlist):
            ch._overview_widget.setParent(None)

        for idx, ch in enumerate(chlist):
            self._gblayout.insertWidget(idx, ch._overview_widget)

    @property
    def polling_rate(self):
        return self._polling_rate

    @polling_rate.setter
    def polling_rate(self, value):
        self._polling_rate = value
        if self._initialized:
            self._polling_rate_label.setText('Polling rate: {0:.2f} Hz'.format(self._polling_rate))

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        self._error_message = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        self._device_id = value

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value

    @property
    def parent(self):
        return parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        if not self._initialized:
            return

        if self._gblayout.parent().title() != self._label:
            self._gblayout.parent().setTitle(self._label)
            for channel_name, channel in self.channels.items():
                channel.update()

    @property
    def pages(self):
        return self._pages

    @property
    def overview_order(self):
        return self._overview_order

    @overview_order.setter
    def overview_order(self, value):
        self._overview_order = value

    def add_page(self, value):
        self._pages.append(value)

    @property
    def channels(self):
        return self._channels

    def get_channel_by_name(self, channel_name):
        try:
            return self._channels[channel_name]
        except:
            return None

    def add_channel(self, channel):
        channel.initialize()
        channel.device_id = self._device_id
        channel.parent_device = self
        self._channels[channel.name] = channel
        self.update()

    def lock(self, message=''):
        """ Disable the device, and display an error message """
        self._error_message = message
        if not self._locked:
            self._overview_widget.show_error_message(self._error_message)
            self._locked = True
            self._sig_update_server.emit()

    def unlock(self):
        if self._locked:
            #self._overview_widget.hide_error_message()
            self._locked = False
            self._sig_update_server.emit()

    @property
    def locked(self):
        return self._locked

    def get_json(self):
        """ Gets a serializable representation of this device """
        properties = {'name': self._name,
                      'label': self._label,
                      'device_id': self._device_id,
                      'driver': self._driver,
                      'channels': {},
                      'overview_order': self._overview_order
                      }

        for channel_name, channel in self._channels.items():
            properties['channels'][channel_name] = channel.get_json()

        return properties #json.dumps(properties)

    def write_json(self, filename):
        myjson = self.get_json()

        with open(filename, "wb") as f:
            f.write(myjson)

    @staticmethod
    def load_from_json(string):
        with open(filename, "rb") as f:
            data = json.load(f)

        filtered_params = {}
        for key, value in data.items():
            if not key == "channels":
                filtered_params[key] = value

        device = Device(**filtered_params)

        for channel_name in data['channels']:
            channel_json = data['channels'][channel_name]
            ch = Channel.load_from_json(channel_json)

            device.add_channel(ch)

        return device
