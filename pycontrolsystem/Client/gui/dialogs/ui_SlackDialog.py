# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SlackDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SlackDialog(object):
    def setupUi(self, SlackDialog):
        SlackDialog.setObjectName("SlackDialog")
        SlackDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SlackDialog.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SlackDialog.sizePolicy().hasHeightForWidth())
        SlackDialog.setSizePolicy(sizePolicy)
        SlackDialog.setMinimumSize(QtCore.QSize(400, 300))
        SlackDialog.setMaximumSize(QtCore.QSize(400, 300))
        self.buttonBox = QtWidgets.QDialogButtonBox(SlackDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(SlackDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 341, 181))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEditToken = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEditToken.setBaseSize(QtCore.QSize(0, 0))
        self.lineEditToken.setObjectName("lineEditToken")
        self.horizontalLayout.addWidget(self.lineEditToken)
        self.btnTestToken = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnTestToken.sizePolicy().hasHeightForWidth())
        self.btnTestToken.setSizePolicy(sizePolicy)
        self.btnTestToken.setMinimumSize(QtCore.QSize(100, 0))
        self.btnTestToken.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnTestToken.setObjectName("btnTestToken")
        self.horizontalLayout.addWidget(self.btnTestToken)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEditChannel = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditChannel.sizePolicy().hasHeightForWidth())
        self.lineEditChannel.setSizePolicy(sizePolicy)
        self.lineEditChannel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineEditChannel.setObjectName("lineEditChannel")
        self.horizontalLayout_2.addWidget(self.lineEditChannel)
        self.btnTestChannel = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.btnTestChannel.setMinimumSize(QtCore.QSize(100, 0))
        self.btnTestChannel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnTestChannel.setObjectName("btnTestChannel")
        self.horizontalLayout_2.addWidget(self.btnTestChannel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_success = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_success.sizePolicy().hasHeightForWidth())
        self.label_success.setSizePolicy(sizePolicy)
        self.label_success.setMinimumSize(QtCore.QSize(320, 50))
        self.label_success.setText("")
        self.label_success.setWordWrap(True)
        self.label_success.setObjectName("label_success")
        self.verticalLayout.addWidget(self.label_success, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

        self.retranslateUi(SlackDialog)
        self.buttonBox.accepted.connect(SlackDialog.accept)
        self.buttonBox.rejected.connect(SlackDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SlackDialog)

    def retranslateUi(self, SlackDialog):
        _translate = QtCore.QCoreApplication.translate
        SlackDialog.setWindowTitle(_translate("SlackDialog", "Set Slack Token..."))
        self.lineEditToken.setText(_translate("SlackDialog", "SLACK TOKEN"))
        self.btnTestToken.setText(_translate("SlackDialog", "Test Token"))
        self.lineEditChannel.setText(_translate("SlackDialog", "SLACK CHANNEL (ID or Name)"))
        self.btnTestChannel.setText(_translate("SlackDialog", "Test Channel"))

