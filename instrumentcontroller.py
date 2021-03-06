import time

from textwrap import dedent

from PyQt5.QtCore import QObject, pyqtSignal

from grblmachine import GrblMachine
from gcodeparams import GcodeParams
from realtimestatus import RealtimeStatus, State

mock = True


class InstrumentController(QObject):
    mill_len_mm = 6
    mill_diam_mm = 3.175
    mill_height_delta = 7

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._machine = GrblMachine()

        # TODO move machine state values into the machine class
        # TODO make classes for all machine state responses
        self._deltaX = 10.0  # mm
        self._deltaY = 10.0
        self._deltaZ = 10.0

        self.feed_rate = 150

        self.probe_x = 0.0
        self.probe_y = 0.0
        self.probe_z = 0.0

        self.state = 'Idle'

        self._null_x = 0.0
        self._null_y = 0.0

        self.is_calibrated_x = False
        self.is_calibrated_y = False
        self.is_calibrated_z = False

        self._calib_state = None
        self._rt_state = RealtimeStatus.default()

    def findDevices(self, token, **kwargs):
        return self._findMachive() and self._findFreqCounter()

    def _findMachive(self):
        return bool(self._machine.find())

    def _findFreqCounter(self):
        return True

    def init(self, token, **kwargs):
        print('init machine...')
        return all([
            self._machine.stop_spindle(),
            self._machine.set_feed_rate(150),
            self._machine.send_raw_command('$RST=#'),  # non-standard GCode command: reset G54-G59 coords # TODO wrap raw command into a helper method
            self._machine.select_xy_plane(),
            self._machine.set_unit('mm'),
            self._machine.set_distance_mode('incremental'),
            self._machine.flush_input(),
            True
        ])

    def closeConnections(self):
        self._machine.close()

    def moveCommand(self, axis, delta, feed_rate, token, **kwargs):
        report_fn = kwargs.pop('fn_progress')
        ok, msg = False, ''
        if axis == 'x':
            ok, msg = self._machine.move_x(delta=delta, feed_rate=feed_rate)
        elif axis == 'y':
            ok, msg = self._machine.move_y(delta=delta, feed_rate=feed_rate)
        elif axis == 'z':
            ok, msg = self._machine.move_z(delta=delta, feed_rate=feed_rate)
        self._waitHelper(report_fn)
        return ok, msg

    def moveXMinus(self, token, **kwargs):
        return self.moveCommand(axis='x', delta=-self.deltaX, feed_rate=self.feed_rate, token=token, **kwargs)

    def moveXPlus(self, token, **kwargs):
        return self.moveCommand(axis='x', delta=self.deltaX, feed_rate=self.feed_rate, token=token, **kwargs)

    def moveYMinus(self, token, **kwargs):
        return self.moveCommand(axis='y', delta=-self.deltaY, feed_rate=self.feed_rate, token=token, **kwargs)

    def moveYPlus(self, token, **kwargs):
        return self.moveCommand(axis='y', delta=self.deltaY, feed_rate=self.feed_rate, token=token, **kwargs)

    def moveZMinus(self, token, **kwargs):
        return self.moveCommand(axis='z', delta=-self.deltaZ, feed_rate=self.feed_rate, token=token, **kwargs)

    def moveZPlus(self, token, **kwargs):
        return self.moveCommand(axis='z', delta=self.deltaZ, feed_rate=self.feed_rate, token=token, **kwargs)

    def askG(self, token, **kwargs):
        return self._machine.query_g()

    def askHash(self, token, **kwargs):
        return self._machine.query_hash()

    def askQuestion(self, token, **kwargs):
        return self._machine.query_question()

    def sendRawCommand(self, token, **kwargs):
        command = kwargs.pop('command', '')
        if command:
            return self._machine.send_raw_command(command)
        return False, 'no command supplied, abort'

    def _queryState(self):
        self._machine.flush_input()
        ok, response = self._machine.query_question()
        self._rt_state = RealtimeStatus(response)
        if ok:
            # TODO this is a hack to not break previous state implementation
            self.probe_x = self._rt_state.probe['x']
            self.probe_y = self._rt_state.probe['y']
            self.probe_z = self._rt_state.probe['z']
            self.feed_rate = self._rt_state.feed_rate
            self.state = self._rt_state.state

    def _queryCalibrationsState(self):
        self._machine.flush_input()
        ok, raw = self._machine.query_hash()
        self._calib_state = GcodeParams(raw)

    def _waitHelper(self, report_fn):
        self._queryState()
        while self._rt_state.state == State.Run:
            self._queryState()
            report_fn({})
            time.sleep(0.5)

    def probeGoToNull(self, token, **kwargs):
        null_x = round(self._null_x, 3)
        null_y = round(self._null_y, 3)
        null_z = round(4 - self.probe_z, 3)

        report_fn = kwargs.pop('fn_progress')

        self._machine.flush_input()

        res_move_x = self._machine.move_x(-null_x)
        self.state = 'Run'
        self._waitHelper(report_fn)

        res_move_y = self._machine.move_y(-null_y)
        self.state = 'Run'
        self._waitHelper(report_fn)

        res_move_z = self._machine.move_z(null_z)
        self.state = 'Run'
        self._waitHelper(report_fn)

        return \
            all(r for r, _ in (res_move_x, res_move_y, res_move_z)), ' '.join(m for _, m in (res_move_x, res_move_y, res_move_z))

    def probeCalibrateX(self, token, **kwargs):
        self.is_calibrated_x = False
        report_fn = kwargs.pop('fn_progress')
        print('start calibrate X...')

        self._queryState()
        if self.state != 'Idle':
            return False, 'machine busy'

        self._machine.flush_input()
        self._machine.move_x(-6)
        self._waitHelper(report_fn)

        height = -self.probe_z - self.mill_len_mm
        self._machine.send_raw_command(f'G01 Z{height}')  # TODO switch to move_z helper when feed parameter is implemented
        self._waitHelper(report_fn)

        if not mock:
            self._machine.send_raw_command('G38.2 X0 F10')
        time.sleep(0.5)
        self._waitHelper(report_fn)

        self._machine.move_x(-6)
        self._waitHelper(report_fn)

        self._queryCalibrationsState()
        self.probe_x = self._calib_state.prb['x'] + self.mill_len_mm / 2  # compensate for mill half-diameter

        self._machine.move_z(0)
        self._waitHelper(report_fn)

        self._machine.move(0, 0, 0)
        self._waitHelper(report_fn)
        self._machine.flush_input()

        print('done calibrating X')
        self.is_calibrated_x = True
        report_fn({})
        return self.is_calibrated_x, 'done calibrating X'

    def probeCalibrateY(self, token, **kwargs):
        self.is_calibrated_y = False
        report_fn = kwargs.pop('fn_progress')
        print('start calibrate Y...')

        self._queryState()
        if self.state != 'Idle':
            return False, 'machine busy'

        self._machine.flush_input()
        self._machine.move_y(delta=-6, feed_rate=150)
        self._waitHelper(report_fn)

        height = -self.probe_z - self.mill_len_mm
        self._machine.send_raw_command(f'G01 Z{height}')
        self._waitHelper(report_fn)

        if not mock:
            self._machine.send_raw_command('G38.2 Y0 F10')
        time.sleep(0.5)
        self._waitHelper(report_fn)

        self._machine.move_y(delta=-6, feed_rate=150)
        self._waitHelper(report_fn)

        self._queryCalibrationsState()
        self.probe_x = self._calib_state.prb['y'] + self.mill_len_mm / 2  # compensate for mill half-diameter

        self._machine.move_z(0)
        self._waitHelper(report_fn)

        self._machine.move(0, 0, 0)
        self._waitHelper(report_fn)
        self._machine.flush_input()

        self.is_calibrated_y = True
        print('done calibrating Y')
        report_fn({})
        return self.is_calibrated_y, 'done calibrating Y'

    def probeCalibrateZ(self, token, **kwargs):
        self.is_calibrated_z = False
        report_fn = kwargs.pop('fn_progress')
        print('start calibrate Z...')

        self._queryState()
        if self.state != 'Idle':
            return False, 'machine busy'

        # TODO add error handling, check ok-s for all ops
        self._machine.flush_input()
        ok, _ = self._machine.send_raw_command('G10 L20 P1 X0Y0Z0')  # magic spell to set the null coordinates for G54, TODO use pg.GCodeSet(?)

        self._machine.flush_input()
        ok, _ = self._machine.select_coord_sys_1()  # G54

        self._machine.flush_input()
        if not mock:
            ok, _ = self._machine.send_raw_command('G38.2 Z-10 F10')  # TODO use pg.GCodeStraightProbe

        time.sleep(0.5)
        self._waitHelper(report_fn)  # wait until state register changes upon pin contact

        self._queryCalibrationsState()
        self.probe_z = self._calib_state.g54['z'] - self._calib_state.prb['z']

        self._machine.send_raw_command('G1 X0Y0Z0 F150')
        self._machine.flush_input()

        self.is_calibrated_z = True
        report_fn({})
        print('done calibrating Z')
        return self.is_calibrated_z, 'done calibrating Z'

    def probeSetNull(self, token, **kwargs):
        print('setting new NULL...')

        self._machine.flush_input()
        ok, response = self._machine.query_question()
        if ok:
            state, coords, *rest = response.split('|')  # TODO move to state class
            self.state = state.lstrip('<')
            coords_x, coords_y, coords_z = map(float, coords[5:].split(','))
        else:
            coords_x, coords_y = 0, 0

        self._null_x = coords_x - self.probe_x
        self._null_y = coords_y - self.probe_y

        ok, msg = self.probeGoToNull(token, **kwargs)

        print('done setting new NULL')
        return ok, msg

    def execCutProgram(self, token, **kwargs):
        cuts = kwargs.pop('cuts')
        report_fn = kwargs.pop('fn_progress')
        print('executing cut program...')
        print(f'cuts: {cuts}')
        print(f'token: {token}')

        segm = ((0, 0),  # start points of segments
                (-2.285, 0.225))
        segment = 4170  # lenght of 1 cutting segment
        step = 100  # milling step in um
        n_of_cuts = segment // step
        depth = 9230 - 7000  # depth of PCB in um
        depth_mill = 200  # depth of milling in um

        self._machine.stop_spindle()
        self._machine.set_distance_mode('absolute')
        self._machine.select_coord_sys_2()

        self._machine.move_xy(x=segm[1][0], y=segm[1][1], feed_rate=150)  # go to start of segment (?) TODO use tool length offset command
        self._waitHelper(report_fn)

        self._machine.set_distance_mode('incremental')

        self._machine.move_z(delta=-self.mill_height_delta, feed_rate=150)  # lower to milling position
        self._waitHelper(report_fn)

        self._machine.start_spindle_cw(speed=300)

        def cut_south():
            # TODO wat
            z_value = round((depth + depth_mill) / 1000, 3)
            y_value = round(step / 1000, 3)

            self._machine.move_z(delta=-z_value, feed_rate=15)
            self._machine.move_y(delta=-y_value, feed_rate=10)
            self._machine.move_z(delta=z_value, feed_rate=150)

        def return_to_null():
            print('Returning to null')
            self._machine.set_distance_mode('absolute')
            self._machine.select_coord_sys_1()
            self._machine.move(0, 0, 0, feed_rate=150)
            self._waitHelper(report_fn)

        for i in list(range(n_of_cuts))[:2]:
            self._machine.flush_input()
            cut_south()
            self._waitHelper(report_fn)
            print(f"step {i + 1} done")

        self._machine.set_distance_mode('incremental')
        self._machine.move_z(delta=self.mill_height_delta, feed_rate=150)  # raise from milling position
        self._machine.stop_spindle()

        return_to_null()

        self._waitHelper(report_fn)
        ok, msg = True, 'ok'

        print('all cuts finished')
        return ok, msg

    @property
    def deltaX(self):
        return self._deltaX

    @deltaX.setter
    def deltaX(self, value):
        self._deltaX = value

    @property
    def deltaY(self):
        return self._deltaY

    @deltaY.setter
    def deltaY(self, value):
        self._deltaY = value

    @property
    def deltaZ(self):
        return self._deltaZ

    @deltaZ.setter
    def deltaZ(self, value):
        self._deltaZ = value

    @property
    def instrumentState(self):
        return dedent(f'''        ??????????????????:
        PRB: {self.state}
        
        ????????????????????:
        X={self.probe_x}
        Y={self.probe_y}
        Z={self.probe_z}
        
        Feed rate:
        FR={self.feed_rate}
        
        ????????????????????:
        X: {self.is_calibrated_x}
        Y: {self.is_calibrated_y}
        Z: {self.is_calibrated_z}''')

    @property
    def calibrationState(self):
        return self._calib_state
