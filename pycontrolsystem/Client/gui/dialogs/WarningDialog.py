from PyQt5.QtWidgets import QDialog
from .ui_WarningDialog import Ui_WarningDialog

class WarningDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.ui = Ui_WarningDialog()
        self.ui.setupUi(self)
        self.ui.lblMessage.setText('Warning: {}'.format(message))
        self.ui.btnClose.clicked.connect(self.on_close_click)
        self.ui.btnIgnore.clicked.connect(self.on_ignore_click)
        self._ignored = False

    def on_close_click(self):
        self.accept()
        self._ignored = False

    def on_ignore_click(self):
        self.accept()
        self._ignored = True

    def exec_(self):
        super(WarningDialog, self).exec_()
        return self._ignored
