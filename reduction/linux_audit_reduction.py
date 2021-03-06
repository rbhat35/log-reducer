import string
import time
import bisect
import copy
import glob
import os
from collections import defaultdict, OrderedDict

from linux_audit_parser import parser, compareTo
from linux_audit_make_final_csv import make_final_csv
from linux_audit_forward_backward_check import forward_check, backward_check


def timed(decorated_fn):
    def wrapper_fn(*args, **kwargs):
        s = time.time()
        retval = decorated_fn(*args, **kwargs)
        e = time.time()
        print decorated_fn, "took", (e-s), "seconds"
        return retval

    return wrapper_fn


def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    else:
        return -1


@timed
def find_lower_upper_limit_of_interval(e_, e, events):
    lower_limit = events[e][0]
    upper_limit = events[e_][1]

    if compareTo(events[e_][0], events[e][0]):
        lower_limit = events[e_][0]
    else:
	print "Error in the order of events!"
    if compareTo(events[e_][1], events[e][1]):
        upper_limit = events[e][1]

    return lower_limit, upper_limit


@timed
#@profile
def reduction(global_list_processed_files_forward, global_list_processed_files_backward, count, incoming_dir):
    # details of csv_details: key-- id; value-- (first col, fourth col, string(forward, backward))
    print "Here in linux"
    print incoming_dir
    forward_files = set(glob.glob(os.path.join(incoming_dir, 'forward-edge-*.csv')))
    backward_files = set(glob.glob(os.path.join(incoming_dir, 'backward-edge-*.csv')))
    print forward_files
    print backward_files
    current_forward_files = forward_files.difference(global_list_processed_files_forward)
    current_backward_files = backward_files.difference(global_list_processed_files_backward)

    if len(current_forward_files) != 0 and len(current_backward_files)!=0:
        global_list_processed_files_forward = \
            global_list_processed_files_forward.union(current_forward_files)
        global_list_processed_files_backward = \
            global_list_processed_files_backward.union(current_backward_files)

        parents, children, events, csv_details, parents_id, children_id = parser(list(current_forward_files), \
            list(current_backward_files))
        parent_ids = []
        stacks = defaultdict(list)
        events = OrderedDict(sorted(events.items(), key = lambda (k, v): v[0]))
        events_final = copy.deepcopy(events)
        for event, time_interval in events.items():
            u, v, sys_call, id_ = event
            if len(stacks[(u, v, sys_call)]) == 0:
                stacks[(u, v, sys_call)].append(event)
            else:
                candidate_event = stacks[(u, v, sys_call)].pop(-1)
                if (forward_check(candidate_event, event, v, children, events) and \
                        backward_check(candidate_event, event, u, parents, events)):
                    lower_limit, upper_limit = find_lower_upper_limit_of_interval(candidate_event, event, events)
                    events[candidate_event] = (lower_limit, upper_limit,) #the lower limit and upper
                    #limit gets updated for the same key as of the popped event
                    events_final[candidate_event] = (lower_limit, upper_limit,)
                    parents_index = index(parents_id[v], id_)
                    if parents_index != -1:
                        del parents[v][parents_index]
                        del parents_id[v][parents_index]
                    children_index = index(children_id[u], id_)
                    if children_index != -1:
                        del children[u][children_index]
                        del children_id[u][children_index]

                    del events_final[event]
                    stacks[(u, v, sys_call)].append(candidate_event)
                else:
                    stacks[(u, v, sys_call)].append(event)

        make_final_csv(events_final, csv_details, count)

    return global_list_processed_files_forward, global_list_processed_files_backward


def main():
    reduction()


if __name__ == '__main__':
    main()
