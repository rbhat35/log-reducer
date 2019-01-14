import csv
import string
import time
import bisect
from collections import defaultdict, OrderedDict

from parser import parser, compareTo

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
def generate_children(node, children):
    for i in children[node]:
        yield i

@timed
def generate_parents(node, parents):
    for i in parents[node]:
        yield i

@timed
def check_overlap(start_1, end_1, start_2, end_2):

    if compareTo(start_1, start_2) and compareTo(end_1, start_2):
        return True
    elif compareTo(end_2, start_1):
        return True

    return False

@timed
def forward_check(e_, e, v, children, events):
    # print "in forward check"
    # print events
    # print "edge 1", e_, events[e_]
    # print "edge 2", e, events[e]

    lower_limit = events[e][0]
    upper_limit = events[e_][0]

    if compareTo(events[e_][0], events[e][0]):
        lower_limit = events[e_][0]
    if compareTo(events[e_][0], events[e][0]):
        upper_limit = events[e][0]

    for child in generate_children(v, children):
        v_child = child[0]
        sys_call = child[1]
        id = child[2]
        if check_overlap(lower_limit, upper_limit, events[(v, v_child, sys_call, id)][0], events[(v, v_child, sys_call, id)][1]) is False:
            return False
    return True

@timed
def backward_check(e_, e, u, parents, events):
    # print u, "nnn",parents, "nnn",events

    lower_limit = events[e][1]
    upper_limit = events[e_][1]

    if compareTo(events[e_][1], events[e][1]):
        lower_limit = events[e_][1]
    if compareTo(events[e_][1], events[e][1]):
        upper_limit = events[e][1]

    for parent in generate_parents(u, parents):
        u_parent = parent[0]
        sys_call = parent[1]
        id = parent[2]
        if check_overlap(lower_limit, upper_limit, events[(u_parent, u, sys_call, id)][0], events[(u_parent, u, sys_call, id)][1]) is False:
            # print "False Returned-Backward"
            return False
    return True

@timed
def merge(e_, e, events):
    lower_limit = events[e][0]
    upper_limit = events[e_][1]

    if compareTo(events[e_][0], events[e][0]):
        lower_limit = events[e_][0]
    if compareTo(events[e_][1], events[e][1]):
        upper_limit = events[e][1]

    #
    # print "Please Merge --", e_, " and ", e, "\n"
    # print "with upper limit as %.07f" % upper_limit
    # print "with lower limit as %.07f" % lower_limit

    return lower_limit, upper_limit

@timed
def make_final_csv(events_final, csv_details):
    with open('forward-reduced.csv', mode='w') as f_forward:
        forward_writer = csv.writer(f_forward, delimiter=',')
        with open('backward-reduced.csv', mode='w') as f_backward:
            backward_writer = csv.writer(f_backward, delimiter=',')
            for k, value in events_final.items():
                u, v, sys_call, id = k
                time_start, time_end = value
                time_start = time_start
                time_end = time_end
                first_col = csv_details[id][0]
                fourth_col = csv_details[id][1]
                tag = csv_details[id][2]
                if tag == 'FORWARD':
                    l = [first_col, v, sys_call, fourth_col, u, time_start, time_end]
                    forward_writer.writerow(l)
                else:
                    l = [first_col, u, sys_call, fourth_col, v, time_start, time_end]
                    backward_writer.writerow(l)
@timed
@profile
def reduction():
    # details of csv_details: key-- id; value-- (first col, fourth col, string(forward, backward))

    parents, children, events, csv_details, parents_id, children_id = parser()
    parent_ids = []
    # print parents
    # print children
    # print events
    stacks = defaultdict(list)
    # parents[v].append((u, sys_call, id))
    # children[u].append((v, sys_call, id))
    # events[(u, v, sys_call, id)] = (time_start, time_start)
    events = OrderedDict(sorted(events.items(), key = lambda (k, v): v[0]))
    events_final = events
    # print events.values()
    for event, time_interval in events.items():
        u, v, sys_call, id_ = event
        if len(stacks[(u, v, sys_call)]) == 0:
            stacks[(u, v, sys_call)].append(event)
        else:
            candidate_event = stacks[(u, v, sys_call)].pop(-1)
            if (forward_check(candidate_event, event, v, children, events) and \
                    backward_check(candidate_event, event, u, parents, events)):
                lower_limit, upper_limit = merge(candidate_event, event, events)
                events[candidate_event] = (lower_limit, upper_limit,) #the lower limit and upper
                #limit gets updated for the same key as of the popped event
                events_final[candidate_event] = (lower_limit, upper_limit,)
		s = time.time()
                parents_index = index(parents_id[v], id_)
                if parents_index != -1:
                    del parents[v][parents_index]
                    del parents_id[v][parents_index]

		e = time.time()
		print "<function 1_for_loop at 0x7f2d0bd670c8> took ", (e - s) ," seconds"
		
		s = time.time()
                children_index = index(children_id[u], id_)
                if children_index != -1:
                    del children[u][children_index]
                    del children_id[u][children_index]
		
		e = time.time()
                print "<function 2_for_loop at 0x7f2d0bd670c8> took ", (e - s) ," seconds"


                # for i, parent in enumerate(parents[v]):
                #     if parent[2] == id_:
                #         del parents[v][i]
                # for i, child in enumerate(children[u]):
                #     if child[2] == id_:
                #         del children[u][i]

                del events_final[event]
                stacks[(u, v, sys_call)].append(candidate_event)
            else:
                stacks[(u, v, sys_call)].append(event)

    make_final_csv(events_final, csv_details)



def main():
    reduction()


if __name__ == '__main__':
    main()
