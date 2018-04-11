# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/PlotChooseDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PlotChooseDialog(object):
    def setupUi(self, PlotChooseDialog):
        PlotChooseDialog.setObjectName("PlotChooseDialog")
        PlotChooseDialog.resize(400, 300)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(12)
        PlotChooseDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(PlotChooseDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeDevices = QtWidgets.QTreeWidget(PlotChooseDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.treeDevices.setFont(font)
        self.treeDevices.setColumnCount(1)
        self.treeDevices.setObjectName("treeDevices")
        self.treeDevices.headerItem().setText(0, "1")
        self.treeDevices.header().setVisible(False)
        self.verticalLayout.addWidget(self.treeDevices)
        self.btnDone = QtWidgets.QPushButton(PlotChooseDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnDone.setFont(font)
        self.btnDone.setObjectName("btnDone")
        self.verticalLayout.addWidget(self.btnDone)

        self.retranslateUi(PlotChooseDialog)
        QtCore.QMetaObject.connectSlotsByName(PlotChooseDialog)

    def retranslateUi(self, PlotChooseDialog):
        _translate = QtCore.QCoreApplication.translate
        PlotChooseDialog.setWindowTitle(_translate("PlotChooseDialog", "Select Channels to Plot"))
        self.btnDone.setText(_translate("PlotChooseDialog", "Done"))

