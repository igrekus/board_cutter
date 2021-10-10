import platform
import serial
import time

from find_device import find_mill_win

msg = []
x_center = 30410  # X cord center in um
y_center = 27530  # Y cord center in um
depth = 9230 - 7000  # depth of PCB in um
depth_mill = 200  # depth of milling in um
step = 100  # milling step in um
segment = 4170  # lenght of 1 cutting segment
N_of_cuts = 0
segm = ((0, 0),  # start points of segments
        (-2.285, 0.225))


def readmsg(lst):
    x = 0
    if ser.inWaiting() == 0:
        lst.insert(x, "Nothing to read")
        return
    while ser.inWaiting() > 0:
        txt = ser.read_until()
        lst.insert(x, txt.decode(encoding="ascii")[0:-1])
        x += 1
        time.sleep(0.1)
    return


def writemsg(txt):
    txt += '\r'
    ser.write(txt.encode(encoding="ascii"))
    time.sleep(0.1)


# extract state from state report (msg=?)
def stateresponde():
    ser.flushInput()
    writemsg("?")
    time.sleep(0.1)
    readmsg(msg)
    txt = msg[0].split('|')
    return (txt[0][1:]).upper()


def cut_South():
    ser.flushInput()
    writemsg("G91")
    writemsg("M3 S300")
    ztxt = "{:.3f}".format(float((depth + depth_mill) / 1000))
    writemsg(f"G1Z-{ztxt} F15")
    txt = "{:.3f}".format(float(step / 1000))
    writemsg(f"G1Y-{txt} F10")
    writemsg(f"G1Z{ztxt} F150")


def cut_Nord():
    ser.flushInput()
    writemsg("G91")
    writemsg("M03 S300")
    ztxt = "{:.3f}".format(float((depth + depth_mill) / 1000))
    writemsg(f"G1Z-{ztxt} F15")
    txt = "{:.3f}".format(float(step / 1000))
    writemsg(f"G1Y{txt} F10")
    writemsg(f"G1Z{ztxt} F150")


def return_to_null():
    writemsg("M5")  # stop spindel
    print("Returning to null")
    writemsg("G90")  # return to null
    writemsg("G54")
    writemsg("G1X0 F150")
    writemsg("G1Y0")
    writemsg("G1Z0")
    while stateresponde() == "RUN": time.sleep(1)


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

writemsg("M5")  # stop spindel if is on
writemsg("$RST=#")  # reset G54-G59 cordinates
writemsg("G17")  # choose XY plane
writemsg("G21")  # choose mm dimension
writemsg("G91")  # incremental movement
writemsg("G10 L20 P1 X0Y0Z0")  # set the null coordinates to G54
ser.flushInput()
# moving to center
writemsg("G1Z10 F150")
txt = "{:.3f}".format(float(y_center / 1000))
writemsg(f"G1Y{txt} F150")
txt = "{:.3f}".format(float(x_center / 1000))
writemsg(f"G1X{txt} F150")
while stateresponde() == "RUN": time.sleep(1)
# writemsg("G1X-0.5 F100")  # move to start position
writemsg("G10 L20 P2 X0Y0Z0")  # set start coordinates to G55
writemsg("G55")  # run in new cordinates
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
    elif txt == "START":
        N_of_cuts = segment // step
        print(N_of_cuts)
        writemsg("M5")  # stop spindel
        ser.flushInput()
        writemsg("G90")
        writemsg("G55")
        writemsg(f"G1X{segm[1][0]}Y{segm[1][1]} F150")  # go to start of segment
        # print(f"G1X{segm[seg][0]}Y{segm[seg][1]} F150")
        writemsg("G91")
        writemsg("G1Z-7 F150")  # going closer down fo 7 mm
        for i in range(N_of_cuts):
            txt = input("Make step?:").upper()
            if txt == 'Y':
                cut_South()
                while stateresponde() == "RUN": time.sleep(1)
                print(f"step {i + 1} done")
            else:
                break
        writemsg("G91")
        writemsg("G1Z7 F150")  # going back up fo 7 mm
        return_to_null()

ser.close()
