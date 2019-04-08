from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QTabBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent
# noinspection PyUnresolvedReferences
# from ui_mainwindow import Ui_MainWindow
import sys


class TabBar(QTabBar):

    sig_move_to_window = pyqtSignal(int, QEvent)

    def __init__(self):
        super().__init__()
        self._drag_active = False
        self._keep_moving = False

    def mousePressEvent(self, event):

        self._drag_active = True
        self._keep_moving = False

        QTabBar.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):

        self._drag_active = False
        self._keep_moving = False

        QTabBar.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):

        if QTabBar.width(self) == event.x() or event.x() == 0 or QTabBar.height(self) == event.y() or event.y() == 0:
            if self._drag_active:
                idx = self.tabAt(event.pos())
                self._keep_moving = True
                self._drag_active = False
                # noinspection PyUnresolvedReferences
                self.sig_move_to_window.emit(idx, event)

        elif self._keep_moving:
            # noinspection PyUnresolvedReferences
            self.sig_move_to_window.emit(-1, event)

        else:

            QTabBar.mouseMoveEvent(self, event)


class TabWindow(QMainWindow):

    sig_move_to_tab = pyqtSignal(QWidget)

    def __init__(self, parent, title, content):

        super().__init__(parent)

        self._title = title
        self._parent = parent

        self.setWindowTitle(title)
        self.setCentralWidget(content)
        self.resize(800, 600)
        self.show()
        self.centralWidget().show()

    def closeEvent(self, event):

        self.sig_move_to_tab.emit(self.centralWidget())
        self._parent.addTab(self.centralWidget(), self.windowTitle())

        event.accept()


class TabWindowWidget(QTabWidget):

    sig_tab_to_window = pyqtSignal(QWidget)
    sig_window_to_tab = pyqtSignal(QWidget)

    def __init__(self, parent):
        super().__init__(parent)
        self.setTabBar(TabBar())  # Override the default QTabBar with our own subclassed TabBar
        # noinspection PyUnresolvedReferences
        self.tabBarDoubleClicked.connect(self.double_click_to_window)
        self.tabBar().sig_move_to_window.connect(self.move_to_window)
        self._newest_window = None
        self.setMovable(True)

    def add_empty_tab(self, name="new_tab", title="New Tab"):
        tab = QWidget()
        tab.setObjectName(name)
        self.addTab(tab, title)

    def double_click_to_window(self, index):

        if self.count() > 1:  # Cannot remove last tab!
            content = self.widget(index)
            title = self.tabBar().tabText(index)
            TabWindow(self, title, content)
            self.sig_tab_to_window.emit(content)

    def move_to_window(self, index, event):
        if index >= 0:
            if self.count() > 1:  # Cannot remove last tab!
                content = self.widget(index)
                title = self.tabBar().tabText(index)
                self._newest_window = TabWindow(self, title, content)
                self._newest_window.sig_move_to_tab.connect(self.moved_to_tab)
                self._newest_window.move(event.globalX()-50, event.globalY()-10)
                self.sig_tab_to_window.emit(content)
        else:
            if self._newest_window is not None:
                self._newest_window.move(event.globalX() - 50, event.globalY() - 10)

    @pyqtSlot(QWidget)
    def moved_to_tab(self, content):
        # Piping through the signal for main GUI
        self.sig_window_to_tab.emit(content)


# class MainWindow(QMainWindow):
#
#     def __init__(self, parent_app):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#
#         self.parent_app = parent_app
#
#         self.tab_window = TabWindowWidget(self.ui.centralwidget)
#         self.tab_window.setObjectName("tabWidget")
#
#         for i in range(3):
#             self.tab_window.add_tab("tab_{}".format(i + 1),
#                                     "Tab {}".format(i + 1))
#
#         self.ui.gridLayout.addWidget(self.tab_window, 0, 0, 1, 1)
#
#         # Connect both close button and QApplication close event to callback_close
#         self.ui.actionClose.triggered.connect(self.close)
#         self.parent_app.aboutToQuit.connect(self.callback_close_event)
#
#     @staticmethod
#     def callback_close_event():
#         print("Called the close_event callback")
#
#
# if __name__ == '__main__':
#
#     app = QApplication(sys.argv)
#     mw = MainWindow(parent_app=app)
#     mw.show()
#     sys.exit(app.exec_())
