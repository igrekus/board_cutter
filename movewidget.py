from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken
from instrumentcontroller import InstrumentController


class MoveWidget(QWidget):

    askFinished = pyqtSignal(bytes)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('movewidget.ui', self)

        self._moveWorker = BackgroundWorker(self)
        self._moveToken = CancelToken()

        self._controller = controller

        self._connectSignals()

    def _connectSignals(self):
        self.askFinished.connect(self.on_askFinished)

    def _moveUp(self):
        self._moveWorker.runTask(
            fn=self._controller.moveUp,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveDown(self):
        self._moveWorker.runTask(
            fn=self._controller.moveDown,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveLeft(self):
        self._moveWorker.runTask(
            fn=self._controller.moveLeft,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveRight(self):
        self._moveWorker.runTask(
            fn=self._controller.moveRight,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveFinishedCallback(self, result: bool):
        if not result:
            print('error during move command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            return
        print('finished moving')

    def _askG(self):
        self._moveWorker.runTask(
            fn=self._controller.askG,
            fn_finished=self.askFinishedCallback,
        )

    def _askHash(self):
        self._moveWorker.runTask(
            fn=self._controller.askHash,
            fn_finished=self.askFinishedCallback,
        )

    def _askQuestion(self):
        self._moveWorker.runTask(
            fn=self._controller.askQuestion,
            fn_finished=self.askFinishedCallback,
        )

    def askFinishedCallback(self, result: bool):
        ok, res = result
        if not ok:
            print('error during ask command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            return

        self.askFinished.emit(res)

    @pyqtSlot(bytes)
    def on_askFinished(self, value):
        self._ui.peditStatus.setPlainText(f'{value.decode("ascii")}\n')

    @pyqtSlot()
    def on_btnUp_clicked(self):
        self._moveUp()

    @pyqtSlot()
    def on_btnDown_clicked(self):
        self._moveDown()

    @pyqtSlot()
    def on_btnLeft_clicked(self):
        self._moveLeft()

    @pyqtSlot()
    def on_btnRight_clicked(self):
        self._moveRight()

    @pyqtSlot()
    def on_btnAskG_clicked(self):
        self._askG()

    @pyqtSlot()
    def on_btnAskHash_clicked(self):
        self._askHash()

    @pyqtSlot()
    def on_btnAskQuestion_clicked(self):
        self._askQuestion()

    @pyqtSlot(int)
    def on_spinUp_valueChanged(self, value):
        self._controller.deltaUp = value

    @pyqtSlot(int)
    def on_spinDown_valueChanged(self, value):
        self._controller.deltaDown = value

    @pyqtSlot(int)
    def on_spinLeft_valueChanged(self, value):
        self._controller.deltaLeft = value

    @pyqtSlot(int)
    def on_spinRight_valueChanged(self, value):
        self._controller.deltaRight = value
