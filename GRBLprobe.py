import platform

import serial
import time

from find_device import find_mill_win

msg = []
probe_x = 0
probe_y = 0
probe_z = 0
X_null = 0
Y_null = 0
step1 = False
step2 = False
step3 = False
mill_len_mm = 6
mill_diam_mm = 3.175


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
    state = (txt[0][1:]).upper()
    return state


# extract cords from state report (msg=?)
def coordresponde():
    ser.flushInput()
    writemsg("?")
    time.sleep(0.1)
    readmsg(msg)
    txt = msg[0].split('|')
    coords = (txt[1][5:]).split(',')
    return coords


# extract X (um) from status report (msg=$#)
def X_status(code):
    ser.flushInput()
    writemsg("$#")
    readmsg(msg)
    for n in range(11):
        txt = msg[n].split(':')
        if txt[0][1:] == code:
            break
    txt2 = txt[1].split(',')  # get list of x y z coords
    return int(float(txt2[0]) * 1000)


# extract Y (um) from status report (msg=$#)
def Y_status(code):
    ser.flushInput()
    writemsg("$#")
    readmsg(msg)
    for n in range(11):
        txt = msg[n].split(':')
        if txt[0][1:] == code:
            break
    txt2 = txt[1].split(',')  # get list of x y z coords
    return int(float(txt2[1]) * 1000)


# extract Z (um) from status report (msg=$#)
def Z_status(code):
    ser.flushInput()
    writemsg("$#")
    readmsg(msg)
    for n in range(11):
        txt = msg[n].split(':')
        if txt[0][1:] == code:
            break
    txt2 = txt[1].split(',')  # get list of x y z coords
    return int(float(txt2[2].replace(']\r', '')) * 1000)


def null_cords():
    global X_null
    global Y_null
    cords = coordresponde()
    X_null = int(float(cords[0]) * 1000) - probe_x
    Y_null = int(float(cords[1]) * 1000) - probe_y


def go_to_null():
    ser.flushInput()
    txt = "{:.3f}".format(float(X_null / 1000))
    # print(f"cmd is G1X-{txt} F150")
    writemsg(f"G1X-{txt} F150")
    while stateresponde() == "RUN":
        # print("doing translate cmd")
        time.sleep(1)
    txt = "{:.3f}".format(float(Y_null / 1000))
    # print(f"cmd is G1Y-{txt} F150")
    writemsg(f"G1Y-{txt} F150")
    while stateresponde() == "RUN":
        # print("doing translate cmd")
        time.sleep(1)
    txt = "{:.3f}".format(float((4000 - probe_z) / 1000))
    # print(f"cmd is G1Z{txt}")
    writemsg(f"G1Z{txt}")
    while stateresponde() == "RUN":
        # print("doing translate cmd")
        time.sleep(0.5)


# connection procedure
ser = None
if platform.system() == 'Darwin':
    while True:
        try:
            ser = serial.Serial(timeout=2, port='/dev/tty.wchusbserial1420', baudrate=115200)
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
writemsg("M5 F150")  # stop spindel if is on
writemsg("$RST=#")  # reset G54-G59 cordinates
writemsg("G17")  # choose XY plane
writemsg("G21")  # choose mm dimension
writemsg("G90")  # absolute cordinates
# readmsg(msg)
# print("After reset")
# print(msg[0])
ser.flushInput()
# writemsg("G1X10Y10Z10 F150") # go to start point
# while stateresponde() == "RUN": # wait until stops
#    time.sleep(1)
# readmsg(msg)
# print("After go")
# print(msg[0])
# ser.flushInput()
# communication proceedure
while True:
    txt = input("Enter command:").upper()
    if txt == "EXIT":
        break
    elif (txt[0] == 'G') or (txt[0] == 'M'):
        writemsg(txt)
        time.sleep(0.1)
        readmsg(msg)
        print(msg[0])
    elif txt == "$G":
        writemsg(txt)
        time.sleep(0.1)
        readmsg(msg)
        print(msg[0])
    elif txt == "STATUS":
        print(f"PRB ststus is {str(probe_x)} {str(probe_y)} {str(probe_z)}")
        # probexyz = xyz_status("G54")
        # print(f"G54 ststus is {str(probexyz[0])} {str(probexyz[0])} {str(probexyz[0])}")
    elif txt == "$#":
        writemsg(txt)
        time.sleep(0.1)
        readmsg(msg)
        for n in range(11):
            print(msg[n])
    elif txt == "NULL":  # go to corrected position
        ser.flushInput()
        txt = "{:.3f}".format(float(X_null / 1000))
        # print(f"cmd is G1X-{txt} F150")
        writemsg(f"G1X-{txt} F150")
        while stateresponde() == "RUN":
            # print("doing translate cmd")
            time.sleep(1)
        txt = "{:.3f}".format(float(Y_null / 1000))
        # print(f"cmd is G1Y-{txt} F150")
        writemsg(f"G1Y-{txt} F150")
        while stateresponde() == "RUN":
            # print("doing translate cmd")
            time.sleep(1)
        txt = "{:.3f}".format(float((4000 - probe_z) / 1000))
        # print(f"cmd is G1Z{txt}")
        writemsg(f"G1Z{txt}")
        while stateresponde() == "RUN":
            # print("doing translate cmd")
            time.sleep(0.5)

    # print("State is:" + stateresponde())
    cords = coordresponde()
    # print(f"X is {cords[0]} Y is {cords[1]} Z is {cords[2]}")

    txt = input("Will make z probe?:").upper()
    if txt == 'Y':
        step1 = True
    # first step: z probing
    if stateresponde() == "IDLE" and step1:
        ser.flushInput()
        writemsg("G10 L20 P1 X0Y0Z0")  # set the null coordinates to G54
        # print("Set the null in G54")
        ser.flushInput()
        writemsg("G54")  # run in new cordinates
        ser.flushInput()
        writemsg("G38.2 Z-10 F10")  # start probing
        time.sleep(0.5)
        while stateresponde() == "RUN":
            # print("Running")
            time.sleep(0.5)
        # print("State is:" + stateresponde())
        step1 = False
        probe_z = Z_status("G54") - Z_status("PRB")  # z in um
        # print(str(probe_z))
        print("Z probe done")
        writemsg("G1 X0Y0Z0 F150")
        ser.flushInput()

    txt = input("Will make x probe?:").upper()
    if txt == 'Y':
        step2 = True
    # second step: x probing
    if stateresponde() == "IDLE" and step2:
        ser.flushInput()
        writemsg("G1X-6 F150")  # go left for mill goin downstairs
        while stateresponde() == "RUN":
            # print("doing translate G1X-10 F150")
            time.sleep(0.5)
        txt = "{:.3f}".format(-float(probe_z) / 1000 - float(mill_len_mm))
        # print(f"cmd is G1Z{str(txt)}")
        writemsg(f"G1Z{str(txt)}")
        while stateresponde() == "RUN":
            # print("doing translate cmd")
            time.sleep(0.5)
        writemsg("G38.2 X0 F10")  # start probing
        time.sleep(0.5)
        while stateresponde() == "RUN":
            # print("Running")
            time.sleep(0.5)
        # print("State is:" + stateresponde())
        writemsg("G1X-6 F150")  # go left for mill going upstairs
        while stateresponde() == "RUN":
            # print("doing translate G1X-6 F150")
            time.sleep(0.5)
        step2 = False
        probe_x = X_status("PRB")
        probe_x += mill_diam_mm * 500  # mill D/2 compensation
        writemsg("G1 Z0")
        while stateresponde() == "RUN":
            # print("doing translate G1 Z0")
            time.sleep(0.5)
        writemsg("G1 X0Y0Z0")
        while stateresponde() == "RUN":
            # print("doing translate G1 X0Y0Z0")
            time.sleep(0.5)
        print("X probe done")
        # print(str(probe_x))
        ser.flushInput()

    txt = input("Will make y probe?:").upper()
    if txt == 'Y':
        step3 = True
    # third step: y probing
    if stateresponde() == "IDLE" and step3:
        ser.flushInput()
        writemsg("G1Y-6 F150")  # go down for mill goin downstairs
        while stateresponde() == "RUN":
            # print("doing translate G1Y-6 F150")
            time.sleep(0.5)
        txt = "{:.3f}".format(-float(probe_z) / 1000 - float(mill_len_mm))
        # print(f"cmd is G1Z{str(txt)}")
        writemsg(f"G1Z{str(txt)}")
        while stateresponde() == "RUN":
            # print("doing translate cmd")
            time.sleep(0.5)
        writemsg("G38.2 Y0 F10")  # start probing
        time.sleep(0.5)
        while stateresponde() == "RUN":
            # print("Running")
            time.sleep(0.5)
        # print("State is:" + stateresponde())
        writemsg("G1Y-6 F150")  # go down for mill going upstairs
        while stateresponde() == "RUN":
            # print("doing translate G1Y-10 F150")
            time.sleep(0.5)
        step3 = False
        probe_y = Y_status("PRB")
        probe_y += mill_diam_mm * 500  # mill D/2 compensation
        writemsg("G1 Z0")
        while stateresponde() == "RUN":
            # print("doing translate G1 Z0")
            time.sleep(0.5)
        writemsg("G1 X0Y0Z0")
        while stateresponde() == "RUN":
            # print("doing translate G1 X0Y0Z0")
            time.sleep(0.5)
        print("Y probe done")
        ser.flushInput()

    # print(f"x: {str(probe_x)} y: {str(probe_y)} z: {str(probe_z)}")
    null_cords()
    # print(f"x: {str(X_null)} y: {str(Y_null)} z: {str(probe_z)}")
    print("Going to start position")
    go_to_null()
ser.close()
