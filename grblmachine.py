import time

from typing import Optional, Tuple

import pygcode as pg
import serial


class GrblMachine:
    baudrate = 115200
    timeout = 2

    def __init__(self):
        self._port: Optional[serial.Serial] = None

    def __str__(self):
        return f'GRBL@{self._port.port}'

    @staticmethod
    def _available_ports_win():
        print('scan COM ports range [1..256]...')
        ports = list()
        for p in [f'COM{i+1}' for i in range(256)]:
            try:
                s = serial.Serial(port=p, baudrate=115200)
                s.close()
                ports.append(p)
                print(f'found port {p}')
            except (OSError, serial.SerialException):
                pass
        return ports

    def find(self):
        for port in self._available_ports_win():
            print(f'ping GRBL at {port}')
            s = serial.Serial(port=port, baudrate=115200, timeout=1)
            if s.is_open:
                s.readall()
                time.sleep(0.5)
                s.write(b'$\n')
                time.sleep(0.5)
                ans = s.readall()
                if b'HLP' in ans:
                    print(f'GRBL found at {port}')
                    self._port = s
                    return True
        else:
            print('GRBL not found, abort')
            return False

    def close(self):
        if self._port is not None and self._port.is_open:
            self._port.close()

    def read(self):
        res = []
        if self._port.inWaiting() != 0:
            res.append(self._port.read_until(expected=b'ok'))
            time.sleep(0.1)
        if res:
            return b''.join(res)
        print('no data available')
        return ''

    def write(self, data):
        data = str(data) + '\n'
        self._port.write(data.encode(encoding="ascii"))

    def flush_input(self):
        print(f'{self} flush input')
        self._port.flushInput()
        return True

    def send(self, command: str):
        print(f'{self} send <<<: {command}')
        self.write(command)
        time.sleep(0.1)
        res = self.read()
        print(f'{self} send >>>: {res}')
        return res.decode('ascii').strip()

    def query(self, question: str):
        print(f'{self} query <<<: {question}')
        self.write(question)
        time.sleep(0.1)
        res = self.read()
        print(f'{self} query >>>: {res}')
        return res.decode('ascii').strip()

    def stop_spindle(self) -> Tuple[bool, str]:
        print('stop spindle...')
        return ('ok' in self.send(str(pg.GCodeStopSpindle()))), ''

    def set_feed_rate(self, value):
        print('set feed rate...')
        return ('ok' in self.send(str(pg.GCodeFeedRate(value)))), ''

    def send_raw_command(self, command):
        print('send raw command defaults...')
        res = self.send(command)
        return ('ok' in res), res

    def select_xy_plane(self):
        print('select XY plane...')
        return ('ok' in self.send(str(pg.GCodeSelectXYPlane()))), ''

    def set_unit(self, unit='mm'):
        print(f'set unit to {unit}...')
        gcode = pg.GCodeUseMillimeters if unit == 'mm' else pg.GCodeUseInches
        return ('ok' in self.send(str(gcode()))), ''

    def set_distance_mode(self, mode='incremental'):
        print(f'set distance mode {mode}')
        if mode != 'incremental':
            raise NotImplementedError(f'GRBL: {mode} not implemented')
        return ('ok' in self.send(str(pg.GCodeIncrementalDistanceMode()))), ''

    # TODO add generic move method with coord params
    # TODO add feed (F) parameter
    def move_x(self, delta):
        print('move X...')
        # TODO hack because lib doesn't support feed rate in linear move commands by default
        command = f'{pg.GCodeLinearMove(X=delta)} {pg.GCodeFeedRate(150)}'
        return ('ok' in self.send(command)), ''

    def move_y(self, delta):
        print('move Y...')
        command = f'{pg.GCodeLinearMove(Y=delta)} {pg.GCodeFeedRate(150)}'
        return ('ok' in self.send(command)), ''

    def move_z(self, delta):
        print('move Z...')
        command = f'{pg.GCodeLinearMove(Z=delta)} {pg.GCodeFeedRate(150)}'
        return ('ok' in self.send(command)), ''

    def query_g(self):
        print('query $G...')
        result = self.query('$G')
        return ('ok' in result), result

    def query_hash(self):
        print('query $#...')
        result = self.query('$#')
        return ('ok' in result), result

    def query_question(self):
        print('query ?...')
        result = self.query('?')
        return ('ok' in result), result
