from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

        self._deltaUp = 10.0  # mm
        self._deltaDown = 10.0
        self._deltaLeft = 10.0
        self._deltaRight = 10.0

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

    def moveUp(self, token, **kwargs):
        return self._machine.move_up(self._deltaUp)

    def moveDown(self, token, **kwargs):
        return self._machine.move_down(self._deltaDown)

    def moveLeft(self, token, **kwargs):
        return self._machine.move_left(self._deltaLeft)

    def moveRight(self, token, **kwargs):
        return self._machine.move_right(self._deltaRight)

    def askG(self, token, **kwargs):
        return self._machine.query_g()

    def askHash(self, token, **kwargs):
        return self._machine.query_hash()

    def askQuestion(self, token, **kwargs):
        return self._machine.query_question()

    @property
    def deltaUp(self):
        return self._deltaUp

    @deltaUp.setter
    def deltaUp(self, value):
        self._deltaUp = value / 1_000  # convert um -> mm

    @property
    def deltaDown(self):
        return self._deltaDown

    @deltaDown.setter
    def deltaDown(self, value):
        self._deltaDown = value / 1_000  # convert um -> mm

    @property
    def deltaLeft(self):
        return self._deltaLeft

    @deltaLeft.setter
    def deltaLeft(self, value):
        self._deltaLeft = value / 1_000  # convert um -> mm

    @property
    def deltaRight(self):
        return self._deltaRight

    @deltaRight.setter
    def deltaRight(self, value):
        self._deltaRight = value / 1_000  # convert um -> mm
