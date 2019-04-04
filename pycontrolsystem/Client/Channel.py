#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Channel representation class

import json
# import datetime
from collections import deque
# Noinspections necessary for PyCharm because installed PyQt5 module is just called 'pyqt'
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, \
    QLabel, QRadioButton, QLineEdit, QPushButton  # , QDial
# noinspection PyPackageRequirements
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from .gui.widgets.DateTimePlotWidget import DateTimePlotWidget
from .gui.widgets.EntryForm import EntryForm
from .gui.widgets.ChannelDial import ChannelDial


class ChannelWidget(QGroupBox):
    _sig_set_value = pyqtSignal(object, object)

    def __init__(self, channel):
        super().__init__(channel.label)
        self._channel = channel

        self._unit_labels = []
        self._write_widget = None
        self._dial_widget = None
        self._read_widget = None

        self.setup()

    @property
    def sig_set_value(self):
        return self._sig_set_value

    def update(self):
        self.setTitle(self._channel.label)
        for label in self._unit_labels:
            label.setText(self._channel.unit)

    def clear(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear(child)

    def setMaximum(self, val):
        # Set maximum value for the dial widget
        # need to disconnect the signal to prevent changing the maximum from emitting a signal
        self._dial_widget.valueChanged.disconnect()
        self._dial_widget.setMaximum(val)
        self._dial_widget.valueChanged.connect(self.set_value_callback)

    def setup(self):
        # clear everything from this widget
        self.clear(self.layout())

        ### HACK -- move the layout to a temp widget, which gets deleted later
        if self.layout() is not None:
            QWidget().setLayout(self.layout())

        if self._channel.data_type == bool:
            hbox_radio = QHBoxLayout()
            self.setLayout(hbox_radio)
            rbon = QRadioButton('On')
            self._write_widget = rbon
            rbon.toggled.connect(self.set_value_callback)
            rboff = QRadioButton('Off')
            rboff.toggle()
            hbox_radio.addWidget(rbon)
            hbox_radio.addWidget(rboff)

        else:
            vbox_readwrite = QVBoxLayout()
            self.setLayout(vbox_readwrite)
            if self._channel.mode in ['write', 'both']:
                # add first row
                hbox_write = QHBoxLayout()
                if self._channel.write_mode == 'text':
                    lblunit = QLabel(self._channel.unit)
                    self._unit_labels.append(lblunit)
                    txtwrite = QLineEdit(str(self._channel.lower_limit))
                    txtwrite.returnPressed.connect(self.set_value_callback)
                    self._write_widget = txtwrite
                    hbox_write.addWidget(self._write_widget)
                    hbox_write.addWidget(lblunit)
                elif self._channel.write_mode == 'dial':
                    dial = ChannelDial(self._channel)
                    dial.setMaximum(10 ** self._channel.precision)
                    self._dial_widget = dial
                    self._dial_widget.valueChanged.connect(self.set_value_callback)
                    hbox_write.addWidget(self._dial_widget)
                vbox_readwrite.addLayout(hbox_write)

            if self._channel.mode in ['read', 'both']:
                # add readonly second row
                hbox_read = QHBoxLayout()
                lblunit = QLabel(self._channel.unit)
                self._unit_labels.append(lblunit)
                txtread = QLineEdit()
                txtread.setDisabled(True)
                self._read_widget = txtread

                hbox_read.addWidget(self._read_widget)
                hbox_read.addWidget(lblunit)
                vbox_readwrite.addLayout(hbox_read)

    def set_value_callback(self):
        if self._channel.data_type == bool:
            val = self._write_widget.isChecked()

        else:
            if self._channel.write_mode == 'text':
                try:
                    val = self._channel.data_type(self._write_widget.text())
                except:
                    print('bad value entered')
                    return

                self._write_widget.setText(str(self._channel.data_type(val)))

            elif self._channel.write_mode == 'dial':
                value = self._dial_widget.value() / float(self._dial_widget.maximum())

                val = (self._channel.upper_limit - self._channel.lower_limit) * value + self._channel.lower_limit

            if val > self._channel.upper_limit or val < self._channel.lower_limit:
                print('value exceeds limits')
                return

        self._sig_set_value.emit(self._channel, val)


class ChannelPlotWidget(QGroupBox):

    def __init__(self, channel):
        super().__init__()

        self._channel = channel
        self.setMinimumSize(350, 300)

        self._plot_item = DateTimePlotWidget(settings=channel.plot_settings)
        self._plot_curve = self._plot_item.curve

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        hbox = QHBoxLayout()
        self._btnpin = QPushButton('Pin')
        self._btnsettings = QPushButton('Settings')
        hbox.addWidget(self._btnsettings)
        hbox.addStretch()
        hbox.addWidget(self._btnpin)
        vbox.addWidget(self._plot_item)
        vbox.addLayout(hbox)

    def clear(self):
        self._plot_item.setData(0, 0)

    @property
    def view_range(self):
        return self._plot_item.viewRange()

    @property
    def plot_item(self):
        return self._plot_item

    @property
    def plot_curve(self):
        return self._plot_curve

    @property
    def btnpin(self):
        return self._btnpin

    @property
    def btnsettings(self):
        return self._btnsettings

    @property
    def settings(self):
        return self._plot_item.settings

    @settings.setter
    def settings(self, newvals):
        self._plot_item.settings = newvals


class Channel(QObject):
    # emits itself and the new value
    _set_signal = pyqtSignal(object, object)

    # emits device and channel
    _pin_signal = pyqtSignal(object, object)

    _settings_signal = pyqtSignal(object)

    _sig_entry_form_ok = pyqtSignal(object, dict)
    _sig_delete = pyqtSignal(object)

    def __init__(self, name='', label='', upper_limit=0.0, lower_limit=0.0,
                 data_type=float, unit="", scaling=1.0, scaling_read=None,
                 mode="both", display_order=0, display_mode="f", precision=2,
                 default_value=0.0, plot_settings=None, stored_values=500,
                 write_mode='text'):

        super().__init__()

        # basic properties
        self._name = name
        self._label = label
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit
        self._data_type = data_type
        self._unit = unit
        self._scaling = scaling
        self._scaling_read = scaling_read
        self._value = default_value
        self._mode = mode
        self._precision = precision
        self._display_mode = display_mode
        self._write_mode = write_mode
        self._display_order = display_order

        # derived properties
        self._displayformat = ".{}{}".format(precision, display_mode)

        # properties that will be set during run time
        self._parent_device = None
        self._locked = False
        if plot_settings is None:
            self._plot_settings = {
                'x': {'mode': 'auto', 'min': 0, 'max': 0, 'log': False,
                      'label': '', 'grid': False},
                'y': {'mode': 'auto', 'min': 0, 'max': 0, 'log': False,
                      'label': '', 'grid': False},
                'widget': {'color': '#ff0000'}
            }
        else:
            self._plot_settings = plot_settings

        self._retain_last_n_values = stored_values
        self._x_values = deque(maxlen=self._retain_last_n_values)
        self._y_values = deque(maxlen=self._retain_last_n_values)

        # entry form representation (settings page in gui)
        self._entry_form = EntryForm(self.label, '',
                                     self.user_edit_properties(), self)
        self._entry_form.sig_save.connect(self.save_changes)
        self._entry_form.sig_delete.connect(self.delete)

        self._initialized = False

    @property
    def initialized(self):
        return self._initialized

    def initialize(self):
        """ create widgets for this channel """
        self._initialized = True

        self._entry_form.add_delete_button()

        # overview widget
        self._overview_widget = ChannelWidget(self)
        self._overview_widget.sig_set_value.connect(self.set_value_callback)

        # plot widget
        self._plot_widget = ChannelPlotWidget(self)
        self._plot_curve = self._plot_widget.plot_curve

        self._plot_widget.btnpin.clicked.connect(self.set_pin_callback)
        self._plot_widget.btnsettings.clicked.connect(self.settings_callback)

    @property
    def plot_widget(self):
        return self._plot_widget

    # ---- entry form ----

    def reset_entry_form(self):
        self._entry_form.properties = self.user_edit_properties()
        self._entry_form.reset()

    @property
    def entry_form(self):
        return self._entry_form.widget

    @pyqtSlot(dict)
    def save_changes(self, newvals):
        """ validates the user data entered into the channel's entry form. 
            returns a dictionary of values to update if there are no errors. """
        data_type_map = {'Float': float, 'Int': int, 'Bool': bool}
        display_mode_map = {'Float': 'f', 'Scientific': 'e'}
        data_type = data_type_map[newvals['data_type']]

        validvals = {}
        for prop_name, val in newvals.items():
            if prop_name in ['lower_limit', 'upper_limit']:
                try:
                    value = data_type(val)
                except:
                    print('bad value entered for limits')
                    return
            elif prop_name == 'scaling':
                try:
                    value = float(val)
                except:
                    print('bad value entered for scaling')
            elif prop_name in ['stored_values', 'precision', 'display_order']:
                try:
                    value = int(val)
                except:
                    print('{} must be int.'.format(prop_name))
                    return
            elif prop_name == 'display_mode':
                value = display_mode_map[val]
            elif prop_name == 'mode':
                value = val.lower()
            elif prop_name == 'write_mode':
                value = val.lower()
            elif prop_name == 'data_type':
                value = data_type
            elif prop_name == 'unit':
                value = val
            else:
                if val != '':
                    value = val
                else:
                    print('no value entered for {}.'.format(prop_name))
                    return

            validvals[prop_name] = value

        self._sig_entry_form_ok.emit(self, validvals)
        self._overview_widget.setup()

    @property
    def sig_entry_form_ok(self):
        return self._sig_entry_form_ok

    @property
    def sig_delete(self):
        return self._sig_delete

    def user_edit_properties(self):

        return {
            'name': {
                'display_name': 'Name',
                'entry_type': 'text',
                'value': self._name,
                'display_order': 1
            },
            'label': {
                'display_name': 'Label',
                'entry_type': 'text',
                'value': self._label,
                'display_order': 2
            },
            'unit': {
                'display_name': 'Unit',
                'entry_type': 'text',
                'value': self._unit,
                'display_order': 3
            },
            'scaling': {
                'display_name': 'Scaling',
                'entry_type': 'text',
                'value': self._scaling,
                'display_order': 4
            },
            'precision': {
                'display_name': 'Precision',
                'entry_type': 'text',
                'value': self._precision,
                'display_order': 5
            },
            'display_mode': {
                'display_name': 'Display Mode',
                'entry_type': 'combo',
                'value': 'Scientific' if self._display_mode == 'e' else 'Float',
                'defaults': ['Float', 'Scientific'],
                'display_order': 6
            },
            'write_mode': {
                'display_name': 'Write Mode',
                'entry_type': 'combo',
                'value': 'Dial' if self._write_mode == 'dial' else 'Text',
                'defaults': ['Text', 'Dial'],
                'display_order': 7
            },
            'lower_limit': {
                'display_name': 'Lower Limit',
                'entry_type': 'text',
                'value': self._lower_limit,
                'display_order': 8
            },
            'upper_limit': {
                'display_name': 'Upper Limit',
                'entry_type': 'text',
                'value': self._upper_limit,
                'display_order': 9
            },
            'data_type': {
                'display_name': 'Data Type',
                'entry_type': 'combo',
                'value': str(self._data_type).split("'")[1].title(),
                'defaults': ['Float', 'Int', 'Bool'],
                'display_order': 10
            },
            'mode': {
                'display_name': 'Mode',
                'entry_type': 'combo',
                'value': self._mode.title(),
                'defaults': ['Read', 'Write', 'Both'],
                'display_order': 11
            },
            'display_order': {
                'display_name': 'Display Order',
                'entry_type': 'text',
                'value': self._display_order,
                'display_order': 12
            },
            'stored_values': {
                'display_name': '# Stored Values',
                'entry_type': 'text',
                'value': self._retain_last_n_values,
                'display_order': 13
            },
        }

    def delete(self):
        self._sig_delete.emit(self)

    # ---- gui interaction ----

    def update(self):
        """ update the gui representation of this channel """
        self._overview_widget.update()

        self._plot_widget.layout().itemAt(0).widget().setLabel('left', '{} [{}]'.format(self._label, self._unit))
        if self._parent_device is not None:
            if self._parent_device.error_message == '':
                self._plot_widget.setTitle('{}/{}'.format(
                    self._parent_device.label, self._label))
            else:
                self._plot_widget.setTitle('(error) {}/{}'.format(
                    self._parent_device.label, self._label))

    @pyqtSlot(object, object)
    def set_value_callback(self, channel, value):
        """ function called when user enters a value into this channel's write widget """
        self._set_signal.emit(channel, value)

    @pyqtSlot()
    def set_pin_callback(self):
        """ called when user presses the channel's pin button """
        self._pin_signal.emit(self.parent_device, self)

    @pyqtSlot()
    def settings_callback(self):
        self._settings_signal.emit(self)

    @property
    def plot_settings(self):
        return self._plot_settings

    @plot_settings.setter
    def plot_settings(self, newsettings):
        self._plot_settings = newsettings
        self._plot_widget.settings = self._plot_settings

    @property
    def x_values(self):
        return self._x_values

    @property
    def y_values(self):
        return self._y_values

    @property
    def stored_values(self):
        return self._retain_last_n_values

    @stored_values.setter
    def stored_values(self, value):
        n = len(self._x_values)

        if value < n:
            # take last n values of current deque
            x_vals = [self._x_values[i] for i in range(n - value, n)]
            y_vals = [self._y_values[i] for i in range(n - value, n)]
        else:
            x_vals = self._x_values
            y_vals = self._y_values

        self._retain_last_n_values = value
        self._x_values = deque(maxlen=self._retain_last_n_values)
        self._x_values.extend(x_vals)
        self._y_values = deque(maxlen=self._retain_last_n_values)
        self._y_values.extend(y_vals)

    def append_data(self, x, y):
        self._x_values.append(x)
        self._y_values.append(y)

    def clear_data(self):
        self._x_values.clear()
        self._y_values.clear()
        self._plot_widget.clear()  # setdata(0,0)

    # ---- properties ----

    @property
    def read_widget(self):
        return self._overview_widget._read_widget

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        self._precision = precision
        self._displayformat = '.{}{}'.format(self._precision, self._display_mode)
        if self._write_mode == 'dial':
            self._overview_widget.setMaximum(10 ** self._precision)
            # self._overview_widget._dial_widget.setMaximum(10**self._precision)

    @property
    def write_mode(self):
        return self._write_mode

    @write_mode.setter
    def write_mode(self, val):
        self._write_mode = val

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        self._displayformat = '.{}{}'.format(self._precision, self._display_mode)

    @property
    def displayformat(self):
        # should not be edited directly. changed when precision is changed
        return self._displayformat

    def lock(self):
        if not self._locked:
            if not self._overview_page_display.locked():
                self._overview_page_display.lock()
                self._locked = True

    def unlock(self):
        if self._locked:
            if self._overview_page_display.locked():
                self._overview_page_display.unlock()
                self._locked = False

    @property
    def locked(self):
        return self._locked

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, device_id):
        self._device_id = device_id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value_to_set):
        if not self._locked:
            self._value = value_to_set

    def read_value(self):
        if not self._locked:
            return self._value

    @property
    def display_order(self):
        return self._display_order

    @display_order.setter
    def display_order(self, value):
        self._display_order = value

    @property
    def parent_device(self):
        return self._parent_device

    @parent_device.setter
    def parent_device(self, device):
        self._parent_device = device
        if self._initialized:
            self.update()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        if self._initialized:
            if self._overview_widget.title() != self._label:
                self._overview_widget.setTitle(self._label)
                self.update()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def upper_limit(self):
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, value):
        self._upper_limit = value

    @property
    def lower_limit(self):
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, value):
        self._lower_limit = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if value not in [bool, int, float]:
            return
        self._data_type = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        if len(str(value)) > 5:
            return
        self._unit = str(value)

    @property
    def scaling(self):
        return self._scaling

    @scaling.setter
    def scaling(self, value):
        self._scaling = value

    def scaling_read(self):
        return self._scaling_read

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ['read', 'write', 'both']:
            return
        self._mode = value

    def get_print_str(self):
        # TODO: Update formatting and add set value to string (how to best get it?). -DW
        fmt = '{:' + self.displayformat + '}'
        val = str(fmt.format(self.value))
        return "\tChannel {}: Read: {} {}\n".format(self.label, val, self.unit)

    def get_json(self):

        properties = {'name': self._name,
                      'label': self._label,
                      'upper_limit': self._upper_limit,
                      'lower_limit': self._lower_limit,
                      'data_type': str(self._data_type),
                      'unit': self._unit,
                      'scaling': self._scaling,
                      'scaling_read': self._scaling_read,
                      'mode': self._mode,
                      'precision': self._precision,
                      'display_mode': self._display_mode,
                      'display_order': self._display_order,
                      'plot_settings': self._plot_settings,
                      'stored_values': self._retain_last_n_values,
                      'write_mode': self._write_mode,
                      }

        return properties  # json.dumps(properties)

    @staticmethod
    def load_from_json(channel_json):

        properties = json.loads(channel_json)

        data_type_str = properties['data_type']

        properties['data_type'] = eval(data_type_str.split("'")[1])

        return channel(**properties)
