from PyQt5.QtWidgets import QDialog
from .ui_ErrorDialog import Ui_ErrorDialog

class ErrorDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.ui = Ui_ErrorDialog()
        self.ui.setupUi(self)
        self.ui.lblMessage.setText('Error: {}'.format(message))
        self.ui.btnClose.clicked.connect(self.on_close_click)

    def on_close_click(self):
        self.accept()
