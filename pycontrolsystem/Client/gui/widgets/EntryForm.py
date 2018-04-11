#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Device/channel entry form

from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
                            QLineEdit, QLabel, QPushButton, QComboBox, \
                            QFrame, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

class EntryForm(QWidget):

    _sig_save_changes = pyqtSignal(dict)
    _sig_delete = pyqtSignal()

    def __init__(self, title, subtitle, properties, parent=None):
        super().__init__()
        self._title = title
        self._subtitle = subtitle
        self._properties = properties
        self._parent = parent

        self._property_list = sorted([(name, x) for name, x in self._properties.items()],
                                     key=lambda y: y[1]['display_order'])

        # create the entry form widget
        self._widget_layout = QGridLayout()

        for i, prop in enumerate(self._property_list):
            lbl = QLabel(prop[1]['display_name'])

            self._widget_layout.addWidget(lbl, i, 0)

            if prop[1]['entry_type'] == 'text':
                txt = QLineEdit(str(prop[1]['value']))
                self._widget_layout.addWidget(txt, i, 1)

            elif prop[1]['entry_type'] == 'combo':
                cb = QComboBox()
                cb.addItems(prop[1]['defaults'])
                cb.setCurrentIndex(prop[1]['defaults'].index(prop[1]['value']))
                self._widget_layout.addWidget(cb, i, 1)

        self._widget = QFrame()
        self._layout = QVBoxLayout()
        self._widget.setLayout(self._layout)

        self._lblTitle = QLabel(self._title)
        font = QFont()
        font.setPointSize(14)
        self._lblTitle.setFont(font)

        self._lblSubtitle = QLabel(self._subtitle)
        btnSave = QPushButton('Save Changes')
        btnSave.clicked.connect(self.on_save_changes_click)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btnSave)
        hbox.addStretch()

        self._layout.addWidget(self._lblTitle)
        self._layout.addWidget(self._lblSubtitle)
        self._layout.addLayout(self._widget_layout)
        self._layout.addLayout(hbox)
        self._layout.addStretch()

    def reset(self):

        for i, prop in enumerate(self._property_list):

            widget = self._widget_layout.itemAt(1 + 2 * i).widget()

            if prop[0] == 'label':
                self._title = prop[1]['value']
                self._lblTitle.setText(self._title)

            if prop[1]['entry_type'] == 'text':
                widget.setText(str(prop[1]['value']))

            elif prop[1]['entry_type'] == 'combo':
                widget.setCurrentIndex(prop[1]['defaults'].index(prop[1]['value']))

    def add_delete_button(self):

        btnDelete = QPushButton('Delete')
        btnDelete.clicked.connect(self.on_delete_click)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(btnDelete)
        hbox.addStretch()
        self._layout.addLayout(hbox)

    @pyqtSlot()
    def on_save_changes_click(self):
        newvals = {}
        for i, prop in enumerate(self._property_list):
            widget = self._widget_layout.itemAt(2 * i + 1).widget()
            if prop[1]['entry_type'] == 'text':
                val = widget.text().strip()
            elif prop[1]['entry_type'] == 'combo':
                val = widget.currentText()

            newvals[prop[0]] = val

        self._sig_save_changes.emit(newvals)

    @pyqtSlot()
    def on_delete_click(self):
        self._sig_delete.emit()

    @property
    def widget(self):
        return self._widget

    @property
    def sig_save(self):
        return self._sig_save_changes

    @property
    def sig_delete(self):
        return self._sig_delete

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, props):
        self._properties = props
        self._property_list = sorted([(name, x) for name, x in self._properties.items()],
                                     key=lambda y: y[1]['display_order'])
