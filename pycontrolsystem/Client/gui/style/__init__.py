# -*- coding: utf-8 -*-
import platform
import os

# Noinspections necessary for PyCharm because installed PyQt5 module is just called 'pyqt'
# noinspection PyPackageRequirements
from PyQt5.QtCore import QFile, QTextStream


def dark_stylesheet():

    f = QFile(os.path.join(os.path.abspath(os.path.dirname(__file__)), "dark_alt/style.qss"))

    if not f.exists():

        return ""

    else:

        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()

        if platform.system().lower() == 'darwin':  # see issue #12 on github

            mac_fix = '''
            QDockWidget::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }
            '''
            stylesheet += mac_fix

        return stylesheet
