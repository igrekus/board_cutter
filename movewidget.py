from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken, TaskResult
from instrumentcontroller import InstrumentController


class MoveWidget(QWidget):

    commStarted = pyqtSignal()
    commFinished = pyqtSignal()

    moveFinished = pyqtSignal(TaskResult)

    reportCoord = pyqtSignal(dict)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('movewidget.ui', self)

        self._worker = BackgroundWorker(self)
        self._token = CancelToken()

        self._controller = controller

        self._connectSignals()

        self._init()

    def _init(self):
        self._ui.peditStatus.setPlainText(self._controller.probeState)

    def _connectSignals(self):
        self.moveFinished.connect(self.on_moveFinished)
        self.reportCoord.connect(self.on_reportCoord)

    # worker dispatch
    def _startWorker(self, fn, cb, prg=None, **kwargs):
        self._worker.runTask(fn=fn, fn_finished=cb,fn_progress=prg, **kwargs)
        self.commStarted.emit()

    def _moveXMinus(self):
        self._startWorker(
            fn=self._controller.moveXMinus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveXPlus(self):
        self._startWorker(
            fn=self._controller.moveXPlus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveYMinus(self):
        self._startWorker(
            fn=self._controller.moveYMinus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveYPlus(self):
        self._startWorker(
            fn=self._controller.moveYPlus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveZMinus(self):
        self._startWorker(
            fn=self._controller.moveZMinus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveZPlus(self):
        self._startWorker(
            fn=self._controller.moveZPlus,
            cb=self._moveFinishedCallback,
            prg=self._reportCoord,
        )

    def _moveFinishedCallback(self, result: tuple):
        self.moveFinished.emit(TaskResult(*result))

    def _reportCoord(self, data):
        self.reportCoord.emit(data)

    @pyqtSlot(TaskResult)
    def on_moveFinished(self, result):
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
        self._ui.peditStatus.setPlainText(self._controller.probeState)

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

    @pyqtSlot(int)
    def on_spinPlane_valueChanged(self, value):
        self._controller.deltaX = value
        self._controller.deltaY = value

    @pyqtSlot(int)
    def on_spinZ_valueChanged(self, value):
        self._controller.deltaZ = value
