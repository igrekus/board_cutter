import platform
import serial
import time

from find_device import find_mill_win

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
    txt += '\r'
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
    ser = find_mill_win()

if not ser:
    raise RuntimeError('No device found')


txt = input("Enter smth:")
time.sleep(0.5)
readmsg(msg)
try:
    print(msg[0])
    print(msg[1])
except LookupError:
    pass
writemsg("M5") #stop spindel if is on
writemsg("$RST=#") #reset G54-G59 cordinates
writemsg("G17") #choose XY plane
writemsg("G21") #choose mm dimension
writemsg("G91") #incremental movement
ser.flushInput()
while True:
    txt = input("Enter command:").upper()
    if txt == "EXIT":
        break
    elif (txt[0] == 'G') or (txt[0] == 'M'):
        writemsg(txt)
        readmsg(msg)
        print(msg[0])
    elif txt == "$G":
        writemsg(txt)
        readmsg(msg)
        print(msg[0])
    elif txt == "$#":
        writemsg(txt)
        readmsg(msg)
        for n in range(12):
            print(msg[n])
    elif txt == '?':
        writemsg(txt)
        readmsg(msg)
        print(msg[0])

ser.close()
