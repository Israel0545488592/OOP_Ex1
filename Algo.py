import json
import csv
import Elevator
import Call


def get_flow(self, path):
    rows = []

    try:
        with open(path, 'r') as fl:
            csvr = csv.reader(fl)
            for row in csvr:
                rows.append(row)
    except IOError as e:
        print(e)

    return rows


def write_answers(data, output):
    try:
        with open(output, 'w') as fl:
            csvw = csv.writer(fl)
            csvw.writerows(data)
    except IOError as e:
        print(e)


def initiate_elevator(data):
    elev = Elevator.Elevator()
    elev.speed = data[1]
    elev.closeTime = data[4]
    elev.openTime = data[5]
    elev.startTime = data[6]
    elev.stopTime = data[7]
    return elev

def addAscend(lst, val):
    i = 0
    while lst[i] < val:
        i +=1
    lst.insert(i, val)

def addDescend(lst, val):
    i = 0
    while lst[i] > val:
        i += 1
    lst.insert(i, val)


class Building:

    def __init__(self, building):

        initiation_data = {}
        try:
            with open(building, "r+") as r:
                initiation_data = json.load(r)
        except IOError as e:
            print(e)

        self.min = initiation_data["_minFloor"]
        self.max = initiation_data["_maxFloor"]

        self.elevators = []
        elevators_data = initiation_data["_elevators"]
        for i in range(len(elevators_data)):
            self.elevators.append(initiate_elevator(list(elevators_data[i].values())))

        self.control_panel = []
        for i in range(len(self.elevators)):
            l = []
            self.control_panel.append(l)

    def travel_time(self, elev_num, call: Call):
        time = 0
        source = self.elevators[elev_num].flour
        missions = self.control_panel[elev_num]

        if self.elevators[elev_num].state == 1:
            i = 0
            while (i < len(missions)) & (missions[i] < call.src):
                dest = missions[i]
                time += self.elevators[elev_num].time(source, dest)
                source = dest
                i +=1
        else:
            i = 0
            while (i < len(missions)) and (missions[i] > call.src):
                dest = missions[i]
                time += self.elevators[elev_num].time(source, dest)
                source = dest
                i += 1

        time += self.elevators[elev_num].time(source, call.src)

        return time

    def activate(self, input, output):  # directories
        time = 0
        flow = get_flow(input)

        for step in flow:
            c = Call.Call(step[2], step[3])
            new_time = step[1]
            dt = new_time - time
            self.recalculate(dt)
            if c.is_legit(self.min, self.max):
                decision = self.assign_fastest_option(c)
                step[5] = decision
            time = new_time

        write_answers(output, flow)

    def assign_fastest_option(self, call: Call):
        c_type = call.type
        c_src = call.src
        c_dest = call.dest
        min_time = self.elevators[0].time(c_src, c_dest)
        min_elev = 0
        # find elevators with same state / at zero state
        for (i, elev) in self.elevators:
            if elev.state == 0:
                curr_time = elev.time(c_src, c_dest)
                if min_time > curr_time:
                    min_time = curr_time
                    min_elev = i
            # for same state check dist, if negative, irrelevant
            elif c_type == elev.state:
                dist = (c_src - elev.floor) * elev.state
                # negates when there's no correlation between dist and state
                if dist > 0:
                    curr_time = elev.time(c_src, c_dest)
                    if min_time > curr_time:
                        min_time = curr_time
                        min_elev = i

        # append Call in control panel
        elev = self.elevators[min_elev]
        elev_missions = self.control_panel[min_elev]
        if elev.state == 1:
            addAscend(elev_missions, c_src)
            addAscend(elev_missions, c_dest)
        elif elev.state == -1:
            addDescend(elev_missions, c_src)
            addDescend(elev_missions, c_dest)
        else:
            elev.state = c_type
            elev_missions.append(c_src)
            elev_missions.append(c_dest)

        return min_elev

    def recalculate(self, dt):  # dt is the passage of time(d - difference)
        for i in range(len(self.control_panel)):
            self.advance(i, dt)

    def advance(self, i, dt):
        elev = self.elevators[i]
        while dt > 0:
            dest = self.control_panel[i][0]

            t = elev.time(elev.flour, dest)
            if t <= dt:
                dt -= t
                elev.flour = dest
                self.control_panel[i].pop(0)
            else:
                if elev.flour - dest < 0:
                    elev.flour += dt * elev.speed
                else:
                    elev.flour -= dt * elev.speed

