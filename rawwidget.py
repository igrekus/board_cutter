from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken, TaskResult
from instrumentcontroller import InstrumentController


class RawWidget(QWidget):

    commStarted = pyqtSignal()
    commFinished = pyqtSignal()
    askFinished = pyqtSignal(TaskResult)
    commandFinished = pyqtSignal(TaskResult)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('rawwidget.ui', self)

        self._worker = BackgroundWorker(self)
        self._token = CancelToken()

        self._controller = controller

        self._connectSignals()

    def _connectSignals(self):
        self.askFinished.connect(self.on_askFinished, type=Qt.QueuedConnection)
        self.commandFinished.connect(self.on_commandFinished, type=Qt.QueuedConnection)

    # worker dispatch
    def _startWorker(self, fn, cb, **kwargs):
        self._worker.runTask(fn=fn, fn_finished=cb, **kwargs)
        self.commStarted.emit()

    def _sendCommand(self):
        self._startWorker(
            fn=self._controller.sendRawCommand,
            cb=self._commandFinishedCallback,
            command=self._ui.editCommand.text()
        )

    def _askG(self):
        self._startWorker(
            fn=self._controller.askG,
            cb=self.askFinishedCallback,
        )

    def _askHash(self):
        self._startWorker(
            fn=self._controller.askHash,
            cb=self.askFinishedCallback,
        )

    def _askQuestion(self):
        self._startWorker(
            fn=self._controller.askQuestion,
            cb=self.askFinishedCallback,
        )

    # callbacks
    def _commandFinishedCallback(self, result: tuple):
        self.commandFinished.emit(TaskResult(*result))

    def askFinishedCallback(self, result: tuple):
        self.askFinished.emit(TaskResult(*result))

    @pyqtSlot(TaskResult)
    def on_commandFinished(self, result):
        ok, msg = result.values
        if not ok:
            print(f'error during raw command: {msg}')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self._ui.peditStatus.setPlainText(f'raw command failed: GRBL {msg}\n')
            self.commFinished.emit()
            return
        self._ui.peditStatus.setPlainText(f'{msg}\n')
        self.commFinished.emit()
        self._ui.editCommand.setFocus()
        self._ui.editCommand.selectAll()

    @pyqtSlot(TaskResult)
    def on_askFinished(self, result: TaskResult):
        ok, msg = result.values
        if not ok:
            print(f'error during ask command, check logs: {msg}')
            # QMessageBox.information(self, 'Внимание', 'Ошибка выполнения запроса к GRBL, подробности в логах.')
            self._ui.peditStatus.setPlainText(f'query command failed: GRBL {msg}\n')
            self.commFinished.emit()
            return
        self._ui.peditStatus.setPlainText(f'{msg}\n')
        self.commFinished.emit()
        self._ui.editCommand.setFocus()
        self._ui.editCommand.selectAll()

    @pyqtSlot()
    def on_btnCommand_clicked(self):
        self._sendCommand()

    @pyqtSlot()
    def on_btnAskG_clicked(self):
        self._askG()

    @pyqtSlot()
    def on_btnAskHash_clicked(self):
        self._askHash()

    @pyqtSlot()
    def on_btnAskQuestion_clicked(self):
        self._askQuestion()

    @pyqtSlot()
    def on_editCommand_returnPressed(self):
        self.on_btnCommand_clicked()
