from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot

from backgroundworker import BackgroundWorker, CancelToken
from instrumentcontroller import InstrumentController
from movewidget import MoveWidget


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('mainwindow.ui', self)

        self._connectWorker = BackgroundWorker(self)
        self._connectToken = CancelToken()

        self._controller = InstrumentController(parent=self)

        # build control widgets
        self._moveWidget = MoveWidget(parent=self, controller=self._controller)

        self._ui.tabMain.addTab(self._moveWidget, 'Перемещение инструмента')

        self._modeBeforeConnect()

    @pyqtSlot()
    def on_btnConnect_clicked(self):
        print('find machine...')
        self._connect()

    def _connect(self):
        self._connectWorker.runTask(
            fn=self._controller.findMachine,
            fn_finished=self._on_connectFinished,
        )

        self._modeDuringConnect()

    def _on_connectFinished(self, result: bool):
        if not result:
            # TODO this crashes if called from another thread, fix somehow
            print('error finding GRBL, check connection')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self._modeBeforeConnect()
            return

        self._initMachine()

    def _initMachine(self):
        self._connectWorker.runTask(
            fn=self._controller.init,
            fn_finished=self._on_initFinished,
        )

    def _on_initFinished(self, result: bool):
        if not result:
            print('error init GRBL, see logs')
            # QMessageBox.information(self, 'Внимание', 'Ошибка инициализации GRBL, подробности в логах.')
            self._modeBeforeConnect()
            return

        self._modeReady()

    def _modeBeforeConnect(self):
        self._ui.tabMain.setEnabled(False)
        self._ui.btnConnect.setEnabled(True)

        self._ui.editAddress.setText('')

    def _modeDuringConnect(self):
        self._ui.tabMain.setEnabled(False)
        self._ui.btnConnect.setEnabled(False)

        self._ui.editAddress.setText('')

    def _modeReady(self):
        self._ui.tabMain.setEnabled(True)
        self._ui.btnConnect.setEnabled(False)

        self._ui.editAddress.setText(str(self._controller._machine))

    def closeEvent(self, arg):
        self._controller.closeConnections()
