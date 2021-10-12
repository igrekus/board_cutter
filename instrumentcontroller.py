from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine


class InstrumentController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

    def findMachine(self, token, **kwargs):
        return bool(self._machine.find())

    def init(self, token, **kwargs):
        print('init machine...')
        return all([
            self._machine.stop_spindle(),
            # self._machine.set_feed_rate(150),
            self._machine.send_raw_command('$RST=#'),  # non-standard GCode command: reset G54-G59 coords
            self._machine.select_xy_plane(),
            self._machine.set_unit('mm'),
            self._machine.set_distance_mode('incremental'),
            self._machine.flush_input(),
        ])

    def closeConnections(self):
        self._machine.close()
