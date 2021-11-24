import platform

import serial
import time

from find_device import find_freq_counter_win

msg = []

def readmsg(lst):
    x=0
    if ser.inWaiting() == 0:
        lst.insert(x,"Nothing to read")
        return
    while ser.inWaiting()>0:
        txt = ser.read_until()
        lst.insert(x, txt.decode(encoding="ascii")[0:-1])
        x += 1
        time.sleep(0.1)
    return

def writemsg(txt):
    txt += '\n'
    ser.write(txt.encode(encoding="ascii"))
    time.sleep(0.1)

# connection procedure
ser = None
if platform.system() == 'Darwin':
    while True:
        try:
            ser=serial.Serial(timeout=2, port='/dev/tty.wchusbserial1420',baudrate=115200)
            ser.close()
            ser.open()
            break
        except FileNotFoundError:
            print("Device is not connected")
        except serial.serialutil.SerialException:
            print("Cant connect to device!")
            txt = input("Wait for input")
elif platform.system() == 'Windows':
    ser = find_freq_counter_win()

if not ser:
    raise RuntimeError('No device found')

txt = input("Enter smth:")
time.sleep(0.5)
ser.flushInput()
while True:
    txt = input("Enter msg:").upper()
    if txt == "EXIT":
        break
    writemsg(txt)
    time.sleep(0.5)
    readmsg(msg)
    print(msg[0])
ser.close()
