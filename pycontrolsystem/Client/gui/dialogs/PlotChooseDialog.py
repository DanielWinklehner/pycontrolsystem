#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Dialog for selecting which channels to plot

# Noinspections necessary for PyCharm because installed PyQt5 module is just called 'pyqt'
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
# noinspection PyPackageRequirements
from PyQt5.QtCore import Qt
from .ui_PlotChooseDialog import Ui_PlotChooseDialog

# from ...Device import Device
# from ...Channel import Channel


class PlotChooseDialog(QDialog):

    def __init__(self, devices, plotted_channels):
        super().__init__()
        self.ui = Ui_PlotChooseDialog()
        self.ui.setupUi(self)
        self.ui.btnDone.clicked.connect(self.on_done_click)

        self._accepted = False  # true if user presses 'done' instead of closing out the window

        self._device_dict = devices
        self._plotted_channels = plotted_channels
        self.update_devices()
        self._selected_channels = []

        # TODO HACK: Gets a list of device objects, assumes these are sorted to get return value
        self._devices = []
        for devname, dev in self._device_dict.items():
            chlist = []
            for chname, ch in reversed(sorted(dev.channels.items(), key=lambda x: x[1].display_order)):
                if ch.data_type == float and ch.mode in ['read', 'both']:
                    chlist.append(ch)
            self._devices.append(chlist)

    def update_devices(self):
        """ Populates tree view with devices/channels """
        for devname, dev in self._device_dict.items():
            devrow = QTreeWidgetItem(self.ui.treeDevices)
            devrow.setFlags(devrow.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            devrow.setText(0, dev.label)
            for chname, ch in reversed(sorted(dev.channels.items(), key=lambda x: x[1].display_order)):
                if ch.data_type == float and ch.mode in ['read', 'both']:
                    chrow = QTreeWidgetItem(devrow)
                    chrow.setFlags(chrow.flags() | Qt.ItemIsUserCheckable)
                    chrow.setText(0, ch.label)
                    # Check the channels that are already enabled on the main window
                    if ch in self._plotted_channels:
                        chrow.setCheckState(0, Qt.Checked)
                    else:
                        chrow.setCheckState(0, Qt.Unchecked)

        self.ui.treeDevices.expandAll()

    def on_done_click(self):
        """ Get selected channels and close the dialog """
        # TODO This section relies on the hack above. It uses indices--Very ugly!
        root_item = self.ui.treeDevices.invisibleRootItem()
        dev_count = root_item.childCount()
        for i in range(dev_count):
            device = self._devices[i]
            dev_item = root_item.child(i)
            ch_count = dev_item.childCount()
            for j in range(ch_count):
                ch_item = dev_item.child(j)
                if ch_item.checkState(0):
                    channel = self._devices[i][j]
                    self._selected_channels.append(channel)

        self._accepted = True
        self.accept()

    def exec_(self):
        super(PlotChooseDialog, self).exec_()
        return (self._accepted, self._selected_channels)
