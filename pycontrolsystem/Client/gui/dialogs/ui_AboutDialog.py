# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(584, 411)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(12)
        AboutDialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.lblLogo = QtWidgets.QLabel(AboutDialog)
        self.lblLogo.setMaximumSize(QtCore.QSize(300, 100))
        self.lblLogo.setText("")
        self.lblLogo.setPixmap(QtGui.QPixmap("../images/mistlogo.png"))
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setObjectName("lblLogo")
        self.horizontalLayout_2.addWidget(self.lblLogo)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.label = QtWidgets.QLabel(AboutDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.btnDone = QtWidgets.QPushButton(AboutDialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnDone.setFont(font)
        self.btnDone.setObjectName("btnDone")
        self.horizontalLayout.addWidget(self.btnDone)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About"))
        self.label.setText(_translate("AboutDialog", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">ControlSystem.py</span></p><p><a href=\"https://github.com/DanielWinklehner/Ion-Source-Control-System\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">https://github.com/DanielWinklehner/Ion-Source-Control-System</span></a></p><p><span style=\" font-size:10pt;\">Control System software for the MIST-1 test beam at MIT</span></p><p><span style=\" font-size:10pt;\">Written for Python 3/PyQt5/PyQtGraph</span></p></body></html>"))
        self.btnDone.setText(_translate("AboutDialog", "Done"))

