import time
from typing import Optional

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
        ports = list()
        for p in [f'COM{i+1}' for i in range(256)]:
            try:
                s = serial.Serial(port=p, baudrate=115200)
                s.close()
                ports.append(p)
            except (OSError, serial.SerialException):
                pass
        return ports

    def find(self):
        for port in self._available_ports_win():
            s = serial.Serial(port=port, baudrate=115200, timeout=0.5)
            if s.is_open:
                s.write(b'<n>')
                time.sleep(0.3)
                ans = s.read(9)
                if b'SPI' in ans:
                    self._port = s
                    return True
        else:
            return False
