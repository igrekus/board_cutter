from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot

from instrumentcontroller import InstrumentController


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('mainwindow.ui', self)
        self._controller = InstrumentController(parent=self)

        self._modeBeforeConnect()
        self._connectSignals()

    def _connectSignals(self):
        self._controller.machineFound.connect(self.on_machineFound)

    @pyqtSlot()
    def on_btnConnect_clicked(self):
        print('find machine...')
        if not self._controller.findMachine():
            QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            return

        self._controller.init()

    @pyqtSlot()
    def on_machineFound(self):
        self._modeReady()

    def _modeBeforeConnect(self):
        self._ui.tabMain.setEnabled(False)
        self._ui.btnConnect.setEnabled(True)

        self._ui.editAddress.setText('')

    def _modeReady(self):
        self._ui.tabMain.setEnabled(True)
        self._ui.btnConnect.setEnabled(False)

        self._ui.editAddress.setText(str(self._controller._machine))

    def closeEvent(self, arg):
        self._controller.closeConnections()
