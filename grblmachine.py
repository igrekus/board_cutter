import time

from typing import Optional

import pygcode as pg
import serial


class GrblMachine:
    baudrate = 115200
    timeout = 2

    def __init__(self):
        self._port: Optional[serial.Serial] = None

    def __str__(self):
        return f'{self.__class__.__name__}@{self._port.port}'

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
        if self._port.is_open:
            self._port.close()
