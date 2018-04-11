#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Handles widget creation in the main window

import time
import copy
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
                            QGroupBox, QLineEdit, QLabel, \
                            QRadioButton, QScrollArea, QPushButton, \
                            QWidget, QSizePolicy, QAction, QTreeWidgetItem, \
                            QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon

from .ui_MainWindow import Ui_MainWindow
from .dialogs.AboutDialog import AboutDialog
from .dialogs.ErrorDialog import ErrorDialog

from .widgets.DateTimePlotWidget import DateTimePlotWidget
from .widgets.EntryForm import EntryForm

from Device import Device
from Channel import Channel
from Procedure import Procedure

class MainWindow(QMainWindow):

    # signal to be emitted when device/channel is changed
    _sig_entry_form_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # aliases
        self._statusbar = self.ui.statusBar
        self._messagelog = self.ui.txtMessageLog
        self._overview = self.ui.fmOverview
        self._plots = self.ui.fmPlots
        self._gbpinnedplot = self.ui.gbPinnedPlot
        self._tabview = self.ui.tabMain
        self._btnload = self.ui.btnLoad
        self._btnsave = self.ui.btnSave
        self._btnquit = self.ui.btnQuit

        # set up pinned plot
        self._pinnedplot = DateTimePlotWidget()
        self._gbpinnedplot.layout().itemAt(0).widget().deleteLater()
        self._gbpinnedplot.layout().insertWidget(0, self._pinnedplot)

        # add a right-aligned About tool bar button
        spc = QWidget()
        spc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        spc.setVisible(True)
        self.ui.toolBar.addWidget(spc)
        self._btnAbout = QAction('About', None)
        self.ui.toolBar.addAction(self._btnAbout)

        # icons
        self._btnquit.setIcon(QIcon(QPixmap('gui/images/icons/process-stop.png')))
        self._btnload.setIcon(QIcon(QPixmap('gui/images/icons/document-open.png')))
        self._btnsave.setIcon(QIcon(QPixmap('gui/images/icons/document-save.png')))
        self._btnAbout.setIcon(QIcon(QPixmap('gui/images/icons/help-browser.png')))
        self.ui.btnExpand.setIcon(QIcon(QPixmap('gui/images/icons/list-add.png')))
        self.ui.btnCollapse.setIcon(QIcon(QPixmap('gui/images/icons/list-remove.png')))

        # dialog connection
        self._btnAbout.triggered.connect(self.show_AboutDialog)

        # tab changes
        self._current_tab = 'main'
        self._tabview.currentChanged.connect(self.tab_changed)

        ## set up containers
        self._overview_layout = QHBoxLayout()
        self._overview.setLayout(self._overview_layout)
        self._overview_layout.addStretch()

        self._plot_layout = QGridLayout()
        self._plots.setLayout(self._plot_layout)

        # settings page
        self.ui.treeDevices.setHeaderLabels(['Label', 'Type'])
        self.ui.treeDevices.currentItemChanged.connect(self.on_settings_row_changed)
        self.ui.btnExpand.clicked.connect(self.ui.treeDevices.expandAll)
        self.ui.btnCollapse.clicked.connect(self.ui.treeDevices.collapseAll)
        self._devvbox = QVBoxLayout()
        self.ui.fmDeviceSettings.setLayout(self._devvbox)

        # local copies of data
        self._settings_devices = {}

    def apply_settings(self, settings):
        self.resize(settings['window-width'], settings['window-height'])

        self.ui.splitMain.setSizes([settings['split-main-first'],
                                    settings['split-main-second']])

        self.ui.splitSettings.setSizes([settings['split-settings-first'],
                                        settings['split-settings-second']])

        self.move(settings['window-pos-x'], settings['window-pos-y'])


    def current_settings(self):
        return {
            'split-main-first': self.ui.splitMain.sizes()[0],
            'split-main-second': self.ui.splitMain.sizes()[1],
            'split-settings-first': self.ui.splitSettings.sizes()[0],
            'split-settings-second': self.ui.splitSettings.sizes()[1],
            'window-maximize-state': True if self.windowState == Qt.WindowMaximized else False,
            'window-pos-x': self.pos().x(),
            'window-pos-y': self.pos().y(),
            'window-width': self.frameSize().width(),
            'window-height': self.frameSize().height(),
            }

    @property
    def current_tab(self):
        return self._current_tab

    def tab_changed(self):
        tabName = self._tabview.tabText(self._tabview.currentIndex())
        if tabName == 'Overview':
            self._current_tab = 'main'
        elif tabName == 'Devices':
            self._current_tab = 'devices'
        elif tabName == 'Plotting':
            self._current_tab = 'plots'

    # ---- Tab Update Functions ----
    def update_overview(self, devices):
        self.clearLayout(self._overview_layout)
        order_devlist = sorted([x for _, x in devices.items()],
                               key=lambda y: y.overview_order)
        for device in order_devlist:
            if 'overview' in device.pages:
                self._overview_layout.insertWidget(0, device._overview_widget)
        self._overview_layout.addStretch()

    def update_plots(self, devices, plotted_channels):
        """ Draw the plotted channels, as specified by the PlotChooseDialog """
        self.clearLayout(self._plot_layout)
        row = 0
        col = 0
        for device_name, device in devices.items():
            for channel_name, channel in device.channels.items():
                if channel in plotted_channels:
                    self._plot_layout.addWidget(channel._plot_widget, row, col)
                    row += 1
                    if row == 2:
                        row = 0
                        col += 1

    def update_device_settings(self, devices):
        """ Populates the treeview on the devices tab """
        self.clearLayout(self._devvbox)
        self.ui.treeDevices.clear()
        for device_name, device in devices.items():
            devrow = QTreeWidgetItem(self.ui.treeDevices)
            devrow.setText(0, device.label)
            devrow.setText(1, 'Device')
            self._settings_devices[device.name] = {'device': device, 'row': devrow, 'channels': {}}
            for chname, ch in reversed(sorted(device.channels.items(), key=lambda x: x[1].display_order)):
                chrow = QTreeWidgetItem(devrow)
                chrow.setText(0, ch.label)
                chrow.setText(1, 'Channel')
                self._settings_devices[device.name]['channels'][ch.name] = {'channel': ch, 'row': chrow}
            newchrow = QTreeWidgetItem(devrow)
            newchrow.setText(0, '[Add a new Channel]')
            #newchrow.setText(1, 'Channel')

        newdevrow = QTreeWidgetItem(self.ui.treeDevices)
        newdevrow.setText(0, '[Add a new Device]')
        #newdevrow.setText(1, 'Device')

        self.ui.treeDevices.expandAll()

    def update_procedures(self, procedures):
        # Add procedures to the procedures tab
        self.clearLayout(self.ui.vboxProcedures)
        for procedure_name, procedure in procedures.items():
            self.ui.vboxProcedures.addWidget(procedure.widget)
        self.ui.vboxProcedures.addStretch()

    # ---- Settings page functions ----
    def on_settings_row_changed(self, item):
        if item == None:
            return

        # if clause fixes mysterious floating entry forms....
        if self._devvbox.count():
            widget = self._devvbox.itemAt(0).widget()
            widget.hide()

        self.clearLayout(self._devvbox)

        obj = None
        parent = None

        for device_name, device_data in self._settings_devices.items():
            # are we editing an existing device/channel?
            if device_data['row'] == item:
                obj = device_data['device']
                break
            else:
                for channel_name, channel_data in device_data['channels'].items():
                    if channel_data['row'] == item:
                        obj = channel_data['channel']
                        parent = device_data['device']
                        break

        if (obj, parent) == (None, None):
            # adding a new device or channel
            if 'channel' in item.text(0).lower():
                for device_name, device_data in self._settings_devices.items():
                    if device_data['row'] == item.parent():
                            parent = device_data['device']
                            break

        if obj is None:
            if parent is None:
                obj = Device(label='New Device')
            else:
                obj = Channel(label='New Channel')
                obj.parent_device = parent

        obj.reset_entry_form()
        self._devvbox.addWidget(obj.entry_form)
        obj.entry_form.show()
        self._sig_entry_form_changed.emit(obj)

    # ---- Misc functions ---
    def show_AboutDialog(self):
        _aboutdialog = AboutDialog()
        _aboutdialog.exec_()

    def show_ErrorDialog(self, error_message='Error'):
        _errordialog = ErrorDialog(error_message)
        _errordialog.exec_()

    def set_polling_rate(self, text):
        self.ui.lblServPoll.setText('Server polling rate: ' + text + ' Hz')

    def status_message(self, text):
        self._statusbar.showMessage(text)
        self._messagelog.append(time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime()) + text)

    @staticmethod
    def clearLayout(layout):
        """ Removes all widgets from a QLayout. Does not delete the widget """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                self.clearLayout(child)
