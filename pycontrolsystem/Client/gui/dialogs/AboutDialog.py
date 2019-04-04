from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from .ui_AboutDialog import Ui_AboutDialog
import os


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._app_path = os.path.abspath(os.path.dirname(__file__))
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self.ui.btnDone.clicked.connect(self.on_done_click)
        logo = QPixmap(os.path.join(self._app_path, '../images/mistlogo.png'))
        self.ui.lblLogo.setPixmap(logo)

    def on_done_click(self):
        self.accept()
