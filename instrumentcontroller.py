from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

        self._deltaX = 10.0  # mm
        self._deltaY = 10.0
        self._deltaZ = 10.0

    def findMachine(self, token, **kwargs):
        return bool(self._machine.find())

    def init(self, token, **kwargs):
        print('init machine...')
        return all([
            # self._machine.stop_spindle(),
            # # self._machine.set_feed_rate(150),
            # self._machine.send_raw_command('$RST=#'),  # non-standard GCode command: reset G54-G59 coords
            # self._machine.select_xy_plane(),
            # self._machine.set_unit('mm'),
            # self._machine.set_distance_mode('incremental'),
            # self._machine.flush_input(),
            True
        ])

    def closeConnections(self):
        self._machine.close()

    def moveXMinus(self, token, **kwargs):
        return self._machine.move_x(-self.deltaX)

    def moveXPlus(self, token, **kwargs):
        return self._machine.move_x(self.deltaX)

    def moveYMinus(self, token, **kwargs):
        return self._machine.move_y(-self.deltaY)

    def moveYPlus(self, token, **kwargs):
        return self._machine.move_y(self.deltaY)

    def moveZMinus(self, token, **kwargs):
        return self._machine.move_z(-self.deltaZ)

    def moveZPlus(self, token, **kwargs):
        return self._machine.move_z(self.deltaZ)

    def askG(self, token, **kwargs):
        return self._machine.query_g()

    def askHash(self, token, **kwargs):
        return self._machine.query_hash()

    def askQuestion(self, token, **kwargs):
        return self._machine.query_question()

    @property
    def deltaX(self):
        return self._deltaX

    @deltaX.setter
    def deltaX(self, value):
        self._deltaX = value / 1_000  # convert um -> mm

    @property
    def deltaY(self):
        return self._deltaY

    @deltaY.setter
    def deltaY(self, value):
        self._deltaY = value / 1_000  # convert um -> mm

    @property
    def deltaZ(self):
        return self._deltaZ

    @deltaZ.setter
    def deltaZ(self, value):
        self._deltaZ = value / 1_000  # convert um -> mm
