import csv
import string
from collections import defaultdict, OrderedDict


FORWARD_CSV_PATH = "/Users/sanyachaba/Desktop/GATECH/Fall 2018/Research/log_compression/parser/forward.csv"
BACKWARD_CSV_PATH = "/Users/sanyachaba/Desktop/GATECH/Fall 2018/Research/log_compression/parser/backwards.csv"

def read_csv(PATH):
    f_csvfile = open(PATH, 'rb')

    f_reader = csv.reader(f_csvfile)
    for row in f_reader:
        yield row

def parser():
    parents = defaultdict(list)
    children = defaultdict(list)
    events = defaultdict(tuple) #make an ordereddict to maintain the order to avoid sorting.
    time = dict()

    id = 0

    f = read_csv(FORWARD_CSV_PATH)
    b = read_csv(BACKWARD_CSV_PATH)

    f_row = next(f, "DONE")
    b_row = next(b, "DONE")

    while f_row is not "DONE" or b_row is not "DONE":
        if b_row is "DONE" or (f_row is not "DONE" and f_row[0] <= b_row[0]):
            v = f_row[1]
            u = f_row[4]
            sys_call = f_row[2]
            time_start = float(f_row[0][:f_row[0].rfind(".")] + str(id))
            f_row = next(f, "DONE")

        else:
            v = b_row[4]
            u = b_row[1]
            sys_call = b_row[2]
            time_start = float(b_row[0][:b_row[0].rfind(".")] + str(id))
            b_row = next(b, "DONE")

        parents[v].append((u, sys_call, id))
        children[u].append((v, sys_call, id))
        events[(u, v, sys_call, id)] = (time_start, time_start)
        id += 1



    return parents, children, events
