from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from backgroundworker import BackgroundWorker, CancelToken, TaskResult
from instrumentcontroller import InstrumentController


class ProbeWidget(QWidget):

    commStarted = pyqtSignal()
    commFinished = pyqtSignal()

    gotToNullFinished = pyqtSignal(TaskResult)
    askCoordFinished = pyqtSignal(TaskResult)
    calibrateFinished = pyqtSignal(TaskResult)

    reportCoord = pyqtSignal(dict)

    def __init__(self, parent=None, controller: InstrumentController=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_QuitOnClose)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # create instance variables
        self._ui = uic.loadUi('probewidget.ui', self)

        self._worker = BackgroundWorker(self)
        self._token = CancelToken()

        self._controller = controller

        self._connectSignals()

        self._init()

    def _init(self):
        # self._askCoord()
        self._ui.peditStatus.setPlainText(self._controller.probeState)

    def _connectSignals(self):
        self.gotToNullFinished.connect(self.on_goToNullFinished)
        self.askCoordFinished.connect(self.on_askCoordFinished)
        self.calibrateFinished.connect(self.on_calibrateFinished)
        self.reportCoord.connect(self.on_reportCoord)

    # worker dispatch
    def _startWorker(self, fn, cb, prg=None, **kwargs):
        self._worker.runTask(fn=fn, fn_finished=cb, fn_progress=prg, **kwargs)
        self.commStarted.emit()

    def _goToNull(self):
        self._startWorker(
            fn=self._controller.probeGoToNull,
            cb=self._goToNullFinishedCallback,
            prg=self._reportCoord,
        )

    def _askCoord(self):
        self._startWorker(
            fn=self._controller.askCoord,
            cb=self._askCoordFinishedCallback,
        )

    def _calibrateZ(self):
        self._startWorker(
            fn=self._controller.probeCalibrateZ,
            cb=self._probeCalibrateFinishedCallback,
            prg=self._reportCoord,
        )

    def _goToNullFinishedCallback(self, result: tuple):
        self.gotToNullFinished.emit(TaskResult(*result))

    def _askCoordFinishedCallback(self, result: tuple):
        self.askCoordFinished.emit(TaskResult(*result))

    def _probeCalibrateFinishedCallback(self, result: tuple):
        self.calibrateFinished.emit(TaskResult(*result))

    def _reportCoord(self, data):
        self.reportCoord.emit(data)

    @pyqtSlot(TaskResult)
    def on_goToNullFinished(self, result):
        ok, _ = result.values
        if not ok:
            print('error during move command, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self.commFinished.emit()
            return
        print('move finished')
        self.commFinished.emit()

    @pyqtSlot(TaskResult)
    def on_askCoordFinished(self, result):
        ok, _ = result.values
        if not ok:
            print('error during coord query, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self.commFinished.emit()
            return
        print(_)
        self.commFinished.emit()

    @pyqtSlot(TaskResult)
    def on_calibrateFinished(self, result):
        ok, _ = result.values
        if not ok:
            print('error during calibrations, check logs')
            # QMessageBox.information(self, 'Внимание', 'Контроллер GRBL не найден, проверьте подключение.')
            self.commFinished.emit()
            return
        self.commFinished.emit()

    @pyqtSlot(dict)
    def on_reportCoord(self, data):
        self._ui.peditStatus.setPlainText(self._controller.probeState)

    @pyqtSlot()
    def on_btnGoToNull_clicked(self):
        self._goToNull()

    @pyqtSlot()
    def on_btnCalibrateZ_clicked(self):
        self._calibrateZ()

