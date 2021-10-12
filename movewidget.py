from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSlot

from backgroundworker import BackgroundWorker, CancelToken
from instrumentcontroller import InstrumentController


class MoveWidget(QWidget):

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('movewidget.ui', self)

        self._moveWorker = BackgroundWorker(self)
        self._moveToken = CancelToken()

        self._controller = controller

    @pyqtSlot()
    def on_btnUp_clicked(self):
        print('move up...')
        self._moveUp()

    def _moveUp(self):
        self._moveWorker.runTask(
            fn=self._controller.findMachine,
            fn_finished=self._on_moveFinished,
        )

    def _on_moveFinished(self, result: bool):
        if not result:
            print('error during move command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self._modeBeforeConnect()
            return
