import csv
import string
from collections import defaultdict, OrderedDict


FORWARD_CSV_PATH = "../parser/backwards.csv"
BACKWARD_CSV_PATH = "../parser/forward.csv"


def compareTo(time1, time2):
    # returns true if time1 <= time2
    start_1_second, start_1_milli, start_1_serial = time1
    start_2_second, start_2_milli, start_2_serial = time2

    return ((start_1_second < start_2_second) or (start_1_second == start_2_second and start_1_milli < start_2_milli) or (start_1_second == start_2_second and start_1_milli == start_2_milli and start_1_serial <= start_2_serial))

def read_csv(PATH):
    f_csvfile = open(PATH, 'rb')

    f_reader = csv.reader(f_csvfile)
    for row in f_reader:
        yield row

def parser():
    parents = defaultdict(list)
    children = defaultdict(list)
    parents_id = defaultdict(list)
    children_id = defaultdict(list)
    events = defaultdict(tuple) #make an ordereddict to maintain the order to avoid sorting.
    meta = defaultdict(tuple)
    time = dict()

    id = 0

    f = read_csv(FORWARD_CSV_PATH)
    b = read_csv(BACKWARD_CSV_PATH)

    f_row = next(f, "DONE")
    b_row = next(b, "DONE")

    while f_row is not "DONE" or b_row is not "DONE":
        if f_row is not "DONE":
            f_milli_ind = f_row[0].rfind(".")
            f_serial_ind = f_row[0].rfind(":")

            f_start_serial = float(f_row[0][f_serial_ind + 1:])
            f_start_milli = float(f_row[0][f_milli_ind + 1 : f_serial_ind])
            f_start_second = float(f_row[0][:f_milli_ind])
        if b_row is not "DONE":
            b_milli_ind = b_row[0].rfind(".")
            b_serial_ind = b_row[0].rfind(":")

            b_start_serial = float(b_row[0][b_serial_ind + 1:])
            b_start_second = float(b_row[0][:b_milli_ind])
            b_start_milli = float(b_row[0][b_milli_ind + 1 : b_serial_ind])

        if b_row is "DONE" or  (f_row is not "DONE" and compareTo((f_start_second, f_start_milli, f_start_serial), (b_start_second, b_start_milli, b_start_serial))):
            v = f_row[1]
            u = f_row[4]
            sys_call = f_row[2]
            time_start = (f_start_second, f_start_milli, f_start_serial)
            metaData = (f_row[0], f_row[3], "FORWARD")
            f_row = next(f, "DONE")

        else:
            v = b_row[4]
            u = b_row[1]
            sys_call = b_row[2]
            time_start = (b_start_second, b_start_milli, b_start_serial)
            metaData = (b_row[0], b_row[3], "BACKWARD")
            b_row = next(b, "DONE")

        parents[v].append((u, sys_call, id))
        parents_id[v].append(id)
        children[u].append((v, sys_call, id))
        children_id[u].append(id)
        events[(u, v, sys_call, id)] = (time_start, time_start)
    	meta[id] = metaData
        id += 1

    return parents, children, events, meta, parents_id, children_id
