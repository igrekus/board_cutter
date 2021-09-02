with open("/Users/Mary/Documents/gcode.txt", 'r') as f:
    i = 0
    for line in f:
        i += 1
        print(f"{i}:" + line)
        for n in line:
            if n == '\n':
                break
            print(n)
        # print(line[:-1])
