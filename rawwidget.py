from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken, TaskResult
from instrumentcontroller import InstrumentController


class RawWidget(QWidget):

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
        self.askFinished.connect(self.on_askFinished)
        self.commandFinished.connect(self.on_commandFinished)

    def _sendCommand(self):
        self._worker.runTask(
            fn=self._controller.sendRawCommand,
            fn_finished=self._commandFinishedCallback,
            command=self._ui.editCommand.text()
        )

    def _commandFinishedCallback(self, result: tuple):
        self.commandFinished.emit(TaskResult(*result))

    def _askG(self):
        self._worker.runTask(
            fn=self._controller.askG,
            fn_finished=self.askFinishedCallback,
        )

    def _askHash(self):
        self._worker.runTask(
            fn=self._controller.askHash,
            fn_finished=self.askFinishedCallback,
        )

    def _askQuestion(self):
        self._worker.runTask(
            fn=self._controller.askQuestion,
            fn_finished=self.askFinishedCallback,
        )

    def askFinishedCallback(self, result: tuple):
        self.askFinished.emit(TaskResult(*result))

    @pyqtSlot(TaskResult)
    def on_commandFinished(self, result):
        ok, msg = result.values
        if not ok:
            print(f'error during raw command: {msg}')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            return
        self._ui.peditStatus.setPlainText(f'{msg.decode("ascii")}\n')

    @pyqtSlot(TaskResult)
    def on_askFinished(self, result: TaskResult):
        ok, data = result.values
        if not ok:
            print('error during ask command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Ошибка выполнения запроса к GRBL, подробности в логах.')
            return
        self._ui.peditStatus.setPlainText(f'{data.decode("ascii")}\n')

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
