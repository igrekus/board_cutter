from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    machineFound = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

    def findMachine(self):
        if not self._machine.find():
            return False
        self.machineFound.emit()
        return True

        self.machineFound.emit()

    def closeConnections(self):
        self._machine.close()

