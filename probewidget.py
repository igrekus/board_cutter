from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken
from instrumentcontroller import InstrumentController


class TaskResult:
    def __init__(self, ok, data):
        self.ok = ok
        self.data = data

    @property
    def values(self):
        return self.ok, self.data


class ProbeWidget(QWidget):

    askFinished = pyqtSignal(TaskResult)
    moveFinished = pyqtSignal(TaskResult)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('probewidget.ui', self)

        self._moveWorker = BackgroundWorker(self)
        self._moveToken = CancelToken()

        self._controller = controller

        self._connectSignals()

    def _connectSignals(self):
        self.askFinished.connect(self.on_askFinished)
        self.moveFinished.connect(self.on_moveFinished)

    def _moveXMinus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveXMinus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveXPlus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveXPlus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveYMinus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveYMinus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveYPlus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveYPlus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveZMinus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveZMinus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveZPlus(self):
        self._moveWorker.runTask(
            fn=self._controller.moveZPlus,
            fn_finished=self._moveFinishedCallback,
        )

    def _moveFinishedCallback(self, result: tuple):
        self.moveFinished.emit(TaskResult(*result))

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

    def askFinishedCallback(self, result: tuple):
        self.askFinished.emit(TaskResult(*result))

    @pyqtSlot(TaskResult)
    def on_moveFinished(self, result):
        ok, _ = result.values
        if not ok:
            print('error during move command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            return
        print('move finished')

    @pyqtSlot(TaskResult)
    def on_askFinished(self, result: TaskResult):
        ok, data = result.values
        if not ok:
            print('error during ask command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Ошибка выполнения запроса к GRBL, подробности в логах.')
            return
        self._ui.peditStatus.setPlainText(f'{data.decode("ascii")}\n')

    @pyqtSlot()
    def on_btnXMinus_clicked(self):
        self._moveXMinus()

    @pyqtSlot()
    def on_btnXPlus_clicked(self):
        self._moveXPlus()

    @pyqtSlot()
    def on_btnYMinus_clicked(self):
        self._moveYMinus()

    @pyqtSlot()
    def on_btnYPlus_clicked(self):
        self._moveYPlus()

    @pyqtSlot()
    def on_btnZMinus_clicked(self):
        self._moveZMinus()

    @pyqtSlot()
    def on_btnZPlus_clicked(self):
        self._moveZPlus()

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
    def on_spinX_valueChanged(self, value):
        self._controller.deltaX = value

    @pyqtSlot(int)
    def on_spinY_valueChanged(self, value):
        self._controller.deltaY = value

    @pyqtSlot(int)
    def on_spinZ_valueChanged(self, value):
        self._controller.deltaZ = value
