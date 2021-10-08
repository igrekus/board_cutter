import serial
import time


def _available_ports_win():
    ports = []
    for p in [f'COM{i+1}' for i in range(256)]:
        try:
            s = serial.Serial(port=p, baudrate=115200)
            s.close()
            ports.append(p)
        except (OSError, serial.SerialException):
            pass
    return ports


def find_mill_win():
    for port in _available_ports_win():
        s = serial.Serial(port=port, baudrate=115200, timeout=1)
        if s.is_open:
            s.readall()
            time.sleep(0.5)
            s.write(b'$\r')
            time.sleep(0.5)
            ans = s.readall()
            if b'HLP' in ans:
                return s
    else:
        raise RuntimeError('No device found')


def find_freq_counter_win():
    for port in _available_ports_win():
        s = serial.Serial(port=port, baudrate=115200, timeout=1)
        if s.is_open:
            s.readall()
            time.sleep(0.5)
            s.write(b'NAME')
            time.sleep(0.5)
            ans = s.readall()
            if b'FreqCount' in ans:
                return s
    else:
        raise RuntimeError('No device found')
