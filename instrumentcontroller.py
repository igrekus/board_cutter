from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    machineFound = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

    def findMachine(self):
        if not self._machine.find():
            raise RuntimeError('No target machine found')

        self.machineFound.emit()
