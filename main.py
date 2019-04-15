
OUT_OF_SYNC = 0
IN_SYNC = 1
countOfLAG = 1
# ------------- Initialization  ----------------#
connect = [[0, 81], [1, 1], [2, 50], [3, 56], [4, 0], [5, 46], [6, 80], [7, 44], [8, 65],
           [9, 84], [10, 39], [11, 66], [12, 105], [13, 63], [14, 100], [15, 79], [16, 58],
           [17, 77], [18, 25], [19, 8], [20, 112], [21, 57], [22, 52], [23, 82], [24, 92],
           [25, 107], [26, 91], [27, 22], [28, 85], [29, 53], [30, 72], [31, 30], [32, 29],
           [33, 54], [34, 26], [35, 115], [36, 86], [37, 116], [38, 3], [39, 97], [40, 76],
           [41, 33], [42, 13], [43, 110], [44, 96], [45, 106], [46, 20], [47, 12], [48, 93],
           [49, 9], [50, 60], [51, 49], [52, 103], [53, 55], [54, 83], [55, 47], [56, 35],
           [57, 114], [58, 108], [59, 23], [60, 51], [61, 21], [62, 101], [63, 19], [64, 40],
           [65, 43], [66, 17], [67, 67], [68, 99], [69, 28], [70, 59], [71, 113], [72, 2],
           [73, 41], [74, 16], [75, 95], [76, 5], [77, 61], [78, 37], [79, 68], [80, 87],
           [81, 6], [82, 70], [83, 71], [84, 69], [85, 73], [86, 78], [87, 88], [88, 48],
           [89, 109], [90, 104], [91, 45], [92, 38], [93, 102], [94, 15], [95, 11], [96, 4],
           [97, 18], [98, 98], [99, 7], [100, 89], [101, 64], [102, 34], [103, 94], [104, 24],
           [105, 27], [106, 32], [107, 74], [108, 10], [109, 62], [110, 14], [111, 111], [112, 75],
           [113, 31], [114, 90], [115, 36], [116, 42]]
ports_A = [0 for i in  range(117)]
ports_B = [0 for i in  range(117)]
not_connect_A = [set() for i in range(117)]
not_connect_B = [set() for i in range(117)]
LAGs = [set() for i in range(10)]

class Port:
    def __init__(self, num, con):
        self.number = num
        self.state = OUT_OF_SYNC
        self.LAG = 0
        self.connectWith = con

    def __str__(self):
        out  = "Number: " + str(self.number) + "\n"
        out += "State: " + str(self.state) + "\n"
        out += "LAG: " + str(self.LAG) + "\n"
        return out

def ReadNotConnect(list, filename):
    file = open(filename, 'r')

    for line in file:
        line = line.replace(' ', '').replace('\n', '').split(':')
        port = int(line[0])
        notconnect = line[1].split(',')
        for badport in notconnect:
            list[port].add(int(badport))

def DefPorts(list, switch):
    for link in connect:
        num = link[switch]
        connectWith = link[1 - switch]
        list[num] = Port(num, connectWith)

def WriteInFile(list, filename):
    out = open(filename, 'w')
    for p in list:
        out.write(p.__str__())
        out.write("\n")

ReadNotConnect(not_connect_A, "NotForA")
ReadNotConnect(not_connect_B, "NotForB")
DefPorts(ports_A, 0)
DefPorts(ports_B, 1)
# -------------       End       ----------------#

# ---------------- Algorithm -------------------#
def StepOnB():
    tempLAG = [set() for i in range(100)]

    for port in ports_A:
        portB = port.connectWith
        LAG = port.LAG
        if not_connect_B[portB].isdisjoint(tempLAG[LAG]):
            tempLAG[LAG].add(portB)
            port.state = IN_SYNC
        else:
            port.state = OUT_OF_SYNC

def FirstStep(current_ports, high_index, current_LAG):
    global countOfLAG

    if len(current_ports) == 0:
        return

    port = list(current_ports)
    port.sort()
    port = port[high_index]

    if current_LAG + 1 >= countOfLAG:
        LAGs.append(set())
        countOfLAG += 1

    if ports_A[port].state and not_connect_A[port].isdisjoint(LAGs[ports_A[port].LAG]):
        LAGs[ports_A[port].LAG].add(port)
        ports_A[port].LAG = ports_A[port].LAG
        current_ports.remove(port)
        SecondStep(current_ports, high_index, current_LAG)
    else:
        ports_A[port].LAG = current_LAG
        buf = set()
        for p in LAGs[current_LAG]:
            ports_A[p].LAG += 1
            buf.add(p)
        LAGs[current_LAG].clear()
        FirstStep(buf, 0, current_LAG + 1)

def SecondStep(current_ports, high_index, current_LAG):

    high_index += 1
    if high_index < len(current_ports):
        ThirdStep(current_ports, high_index, current_LAG)
    else:
        tmp = set()
        for p in current_ports:
            if ports_A[p].LAG > current_LAG:
                tmp.add(p)
        if len(tmp):
            FirstStep(tmp, 0, current_LAG + 1)

def ThirdStep(current_ports, high_index, current_LAG):

    port = list(current_ports)
    port.sort()
    port = port[high_index]
    global countOfLAG

    if ports_A[port].state and not_connect_A[port].isdisjoint(LAGs[ports_A[port].LAG]):
        LAGs[ports_A[port].LAG].add(port)
        ports_A[port].LAG = ports_A[port].LAG
        current_ports.remove(port)
        high_index -= 1
        SecondStep(current_ports, high_index, current_LAG)

    if ports_A[port].state == OUT_OF_SYNC:
        ports_A[port].LAG += 1
        SecondStep(current_ports, high_index, current_LAG)

    if ports_A[port].state and not not_connect_A[port].isdisjoint(LAGs[ports_A[port].LAG]):
        ports_A[port].LAG += 1
        FourthStep(current_ports, high_index, current_LAG)

def FourthStep(current_ports, high_index, current_LAG):

    high_index += 1
    if high_index < len(current_ports):
        FifthStep(current_ports, high_index, current_LAG)
    else:
        tmp = set()
        for p in current_ports:
            if ports_A[p].LAG == current_LAG:
                tmp.add(p)
        if len(tmp):
            ThirdStep(tmp, 0, current_LAG)

def FifthStep(current_ports, high_index, current_LAG):

    port = list(current_ports)
    port.sort()
    port = port[high_index]

    if not_connect_A[port].isdisjoint(LAGs[ports_A[port].LAG]):
        SecondStep(current_ports, high_index, current_LAG)
    else:
        ports_A[port].LAG += 1
        SecondStep(current_ports, high_index, current_LAG)

n = set()
for port in ports_A:
    n.add(port.number)

for i in range(12):
    StepOnB()
    for lag in LAGs:
        lag.clear()
    FirstStep(n.copy(), 0, 0)
# ------------        End     ------------------#


def Processing(mass):
    for i, lag in enumerate(mass):
        lg = list(lag)
        lg.sort()
        mass[i] = lg
    return mass

def CreateLAGforB():
    temp = []
    for i, lag in enumerate(LAGs):
        temp.append([])
        for port in lag:
            temp[i].append(ports_A[port].connectWith)
    return temp

def PrintResult(mass):
    st = ""
    for lag in mass:
        for port in lag:
            st += str(port) + ","
        st = st[:-1] + '|'
    print(st[:-1])

def WriteResult():
    dd = open("Result_A", 'w')
    db = open("Result_B", 'w')
    for i in range(len(LAGs)):
        dd.write(LAGs[i].__str__() + "\n")
        db.write(LAGs_B[i].__str__() + "\n")
    dd.close()
    db.close()
    WriteInFile(ports_A, "Ports v.3")

del LAGs[15]
del LAGs[17]
LAGs = Processing(LAGs)
LAGs_B = Processing(CreateLAGforB())

LAGs.sort(key=lambda val: val[0])
LAGs_B.sort(key=lambda val: val[0])

PrintResult(LAGs)
PrintResult(LAGs_B)
WriteResult()
