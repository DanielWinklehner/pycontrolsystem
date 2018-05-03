# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/WarningDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WarningDialog(object):
    def setupUi(self, WarningDialog):
        WarningDialog.setObjectName("WarningDialog")
        WarningDialog.resize(320, 171)
        self.verticalLayout = QtWidgets.QVBoxLayout(WarningDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 17, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.lblMessage = QtWidgets.QLabel(WarningDialog)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        self.lblMessage.setFont(font)
        self.lblMessage.setAlignment(QtCore.Qt.AlignCenter)
        self.lblMessage.setWordWrap(True)
        self.lblMessage.setObjectName("lblMessage")
        self.verticalLayout.addWidget(self.lblMessage)
        spacerItem1 = QtWidgets.QSpacerItem(20, 4, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.btnIgnore = QtWidgets.QPushButton(WarningDialog)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        self.btnIgnore.setFont(font)
        self.btnIgnore.setObjectName("btnIgnore")
        self.horizontalLayout.addWidget(self.btnIgnore)
        self.btnClose = QtWidgets.QPushButton(WarningDialog)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        self.btnClose.setFont(font)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout.addWidget(self.btnClose)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WarningDialog)
        QtCore.QMetaObject.connectSlotsByName(WarningDialog)

    def retranslateUi(self, WarningDialog):
        _translate = QtCore.QCoreApplication.translate
        WarningDialog.setWindowTitle(_translate("WarningDialog", "Error"))
        self.lblMessage.setText(_translate("WarningDialog", "Error: Object is part of a procedure. Delete the procedure before editing."))
        self.btnIgnore.setText(_translate("WarningDialog", "Ignore"))
        self.btnClose.setText(_translate("WarningDialog", "Cancel"))

