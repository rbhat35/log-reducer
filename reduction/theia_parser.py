import csv
import string
from collections import defaultdict, OrderedDict
import glob
import os
from natsort import natsorted


FORWARD_CSV_PATH = "../data/new-csvs/"
BACKWARD_CSV_PATH = "../data/new-csvs/"


def compareTo(time1, time2):
    # returns true if time1 <= time2
    start_1_second, start_1_milli, start_1_serial = time1
    start_2_second, start_2_milli, start_2_serial = time2

    return ((start_1_second < start_2_second) or (start_1_second == start_2_second and start_1_milli < start_2_milli) or (start_1_second == start_2_second and start_1_milli == start_2_milli and start_1_serial <= start_2_serial))

def read_csv(PATH, pattern):
    all_file_names_list = glob.glob(os.path.join(PATH, pattern))
    all_file_names_list = natsorted(all_file_names_list)

    for filename in all_file_names_list:
        file = open(filename, 'rb')
        f_reader = csv.reader(file, delimiter=',')

        for row in f_reader:
            yield row

def parser():
    parents = defaultdict(list)
    children = defaultdict(list)
    parents_id = defaultdict(list)
    children_id = defaultdict(list)
    events = defaultdict(tuple) # Suggestion: make an ordereddict to maintain the order to avoid sorting.
    sizes = defaultdict(tuple) # maps id to read size
    meta = defaultdict(tuple)
    time = dict()

    f = read_csv(FORWARD_CSV_PATH, 'forward-edge-*.csv')
    b = read_csv(BACKWARD_CSV_PATH, 'backward-edge-*.csv')

    f_row = next(f, "DONE")
    b_row = next(b, "DONE")

    id = 0

    while f_row is not "DONE" or b_row is not "DONE":
        if f_row is not "DONE":
            # Note that the timeStamp is f_row[6]
            f_start_serial = float(f_row[6][13:])
            f_start_milli = float(f_row[6][10:13])
            f_start_second = float(f_row[6][:10])

        if b_row is not "DONE":
            # Note that the timeStamp is b_row[6]
            b_start_serial = float(b_row[6][13:])
            b_start_milli = float(b_row[6][10:13])
            b_start_second = float(b_row[6][:10])


        if b_row is "DONE" or  (f_row is not "DONE" and compareTo((f_start_second, f_start_milli, f_start_serial), (b_start_second, b_start_milli, b_start_serial))):
            sys_call = f_row[2]
            v = f_row[3] # in forward, 'v' is the process, right?
            u = f_row[4] # in forward, 'u' is the file being accessed (resource), right?
            size = f_row[7]
            time_start = (f_start_second, f_start_milli, f_start_serial)

            # metaData contains (RecordType, EventID, ResourceUUID2, timestamp, EventType, "FORWARD")
            # I'm unsure about why there are two EventType entries
            metaData = (f_row[0], f_row[1], f_row[5], f_row[6], f_row[8], "FORWARD")
            f_row = next(f, "DONE")
        else:
            sys_call = b_row[2]
            u = b_row[3] # in backward, 'u' is the process
            v = b_row[4] # in backward, 'v' is the file being accessed (resource)
            size = b_row[7]
            time_start = (b_start_second, b_start_milli, b_start_serial)

            # metaData contains (RecordType, EventID, ResourceUUID2, timestamp, EventType, "BACKWARD")
            # I'm unsure about why there are two EventType entries
            metaData = (b_row[0], b_row[1], b_row[5], b_row[6], b_row[8], "BACKWARD")
            b_row = next(b, "DONE")

        parents[v].append((u, sys_call, id))
        parents_id[v].append(id)
        children[u].append((v, sys_call, id))
        children_id[u].append(id)
        events[(u, v, sys_call, id)] = (time_start, time_start)
        sizes[id] = size
    	meta[id] = metaData

        id += 1

    return parents, children, events, meta, parents_id, children_id, sizes


def debug():
    f = read_csv(FORWARD_CSV_PATH, 'forward-edge-*.csv')
    b = read_csv(BACKWARD_CSV_PATH, 'backward-edge-*.csv')

    for i in range(1):
        b_row = next(b, "DONE")
        id = b_row[1]
        sys_call = b_row[2]
        u = b_row[3] # in backward, 'u' is the process
        v = b_row[4] # in backward, 'v' is the file being accessed (resource)
        size = b_row[7]
        # time_start = (b_start_second, b_start_milli, b_start_serial)

        # f_start_serial = float(timeStamp[13:])
        # f_start_milli = float(timeStamp[10: 13])
        # f_start_second = float(timeStamp[:10])

        print id
        print sys_call
        print u
        print v
        print size
        # print time_start


if __name__ == "__main__":
    # debug()
    parents, children, events, meta, parents_id, children_id, sizes = parser()

    print len(parents)
    print len(children)
    print len(events)
    print len(meta)
    print len(sizes)