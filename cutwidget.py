from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken, TaskResult
from instrumentcontroller import InstrumentController


class CutWidget(QWidget):

    commStarted = pyqtSignal()
    commFinished = pyqtSignal()

    cutFinished = pyqtSignal(TaskResult)

    reportCoord = pyqtSignal(dict)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('cutwidget.ui', self)

        self._worker = BackgroundWorker(self)
        self._token = CancelToken()

        self._controller = controller

        self._connectSignals()

        self._init()

    def _init(self):
        self._ui.peditStatus.setPlainText(self._controller.instrumentState)

    def _connectSignals(self):
        self.cutFinished.connect(self.on_cutFinished, type=Qt.QueuedConnection)
        self.reportCoord.connect(self.on_reportCoord, type=Qt.QueuedConnection)

    # worker dispatch
    def _startWorker(self, fn, cb, prg=None, **kwargs):
        self._worker.runTask(fn=fn, fn_finished=cb,fn_progress=prg, **kwargs)
        self.commStarted.emit()

    def _startCut(self):
        self._startWorker(
            fn=self._controller.moveXMinus,
            cb=self._cutFinishedCallback,
            prg=self._reportCoord,
        )

    def _cutFinishedCallback(self, result: tuple):
        self.cutFinished.emit(TaskResult(*result))

    def _reportCoord(self, data):
        self.reportCoord.emit(data)

    @pyqtSlot(TaskResult)
    def on_cutFinished(self, result):
        ok, _ = result.values
        if not ok:
            print('error during move command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self.commFinished.emit()
            return
        print('move finished')
        self.commFinished.emit()

    @pyqtSlot(dict)
    def on_reportCoord(self, data):
        self._ui.peditStatus.setPlainText(self._controller.instrumentState)

    @pyqtSlot()
    def on_btnStart_clicked(self):
        self._startCut()
