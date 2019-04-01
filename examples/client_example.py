from pycontrolsystem.Client.ControlSystem import ControlSystem
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QApplication
from multiprocessing import freeze_support
import sys


if __name__ == '__main__':
    # Multiprocessing really wants this :P
    freeze_support()

    # Create a QApplication
    app = QApplication([])

    # Create the control system GUI
    cs = ControlSystem(parent_app=app, server_ip='127.0.0.1', server_port=5000, debug=False)
    cs.run()

    # Wrap running the app in a sys.exit call to forward the exit signal
    sys.exit(app.exec_())
