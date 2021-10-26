import time

from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

        self._deltaX = 10.0  # mm
        self._deltaY = 10.0
        self._deltaZ = 10.0

        self._probe_x = 0.0
        self._probe_y = 0.0
        self._probe_z = 0.0

        self._null_x = 0.0
        self._null_y = 0.0

    def findDevices(self, token, **kwargs):
        return self._findMachive() and self._findFreqCounter()

    def _findMachive(self):
        return bool(self._machine.find())

    def _findFreqCounter(self):
        return True

    def init(self, token, **kwargs):
        print('init machine...')
        return all([
            # self._machine.stop_spindle(),
            # # self._machine.set_feed_rate(150),
            # self._machine.send_raw_command('$RST=#'),  # non-standard GCode command: reset G54-G59 coords # TODO wrap raw command into a helper method
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

    def askCoord(self, token, **kwargs):
        ok, string = self._machine.query_question()
        return ok, string

    def sendRawCommand(self, token, **kwargs):
        command = kwargs.pop('command', '')
        if command:
            return self._machine.send_raw_command(command)
        return False, 'no command supplied, abort'

    def probeGoToNull(self, token, **kwargs):
        # TODO move unit conversions to controller
        null_x = round(self._null_x / 1_000, 3)
        null_y = round(self._null_y / 1_000, 3)
        null_z = round((4000 - self._probe_z) / 1_000)

        report_fn = kwargs.pop('fn_progress')

        self._machine.flush_input()

        res_move_x = self._machine.move_x(-null_x)
        response = 'Run'  # TODO move to helper
        while 'Run' in response:
            self._machine.flush_input()
            ok, response = self._machine.query_question()
            if ok:
                x, y, z = response.split('|')[1][5:].split(',')
                report_fn({'coords': f'X={x}\nY={y}\nZ={z}'})
            time.sleep(0.5)

        res_move_y = self._machine.move_y(-null_y)
        response = 'Run'
        while 'Run' in response:
            self._machine.flush_input()
            ok, response = self._machine.query_question()
            if ok:
                x, y, z = response.split('|')[1][5:].split(',')
                report_fn({'coords': f'X={x}\nY={y}\nZ={z}'})
            time.sleep(0.5)

        res_move_z = self._machine.move_z(null_z)
        response = 'Run'
        while 'Run' in response:
            self._machine.flush_input()
            ok, response = self._machine.query_question()
            if ok:
                x, y, z = response.split('|')[1][5:].split(',')
                report_fn({'coords': f'X={x}\nY={y}\nZ={z}'})
            time.sleep(0.5)

        return \
            all(r for r, _ in (res_move_x, res_move_y, res_move_z)), ' '.join(m for _, m in (res_move_x, res_move_y, res_move_z))

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
