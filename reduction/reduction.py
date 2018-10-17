import csv
import string
from collections import defaultdict, OrderedDict

from parser import parser


def generate_children(node, children):
    for i in children[node]:
        yield i

def generate_parents(node, parents):
    for i in parents[node]:
        yield i

def check_overlap(start_1, end_1, start_2, end_2):
    # print start_1, end_1, start_2, end_2
    if start_1 <= start_2:
        print "1"
        if end_1 <= start_2:
            print "2"
            return True
    else:
        if end_2 <= start_1:
            return True
    return False


def forward_check(e_, e, v, children, events):
    # print "in forward check"
    # print events
    # print "edge 1", e_, events[e_]
    # print "edge 2", e, events[e]

    lower_limit = min(events[e_][0], events[e][0])
    upper_limit = max(events[e_][0], events[e][0])
    for child in generate_children(v, children):
        v_child = child[0]
        sys_call = child[1]
        id = child[2]
        if check_overlap(lower_limit, upper_limit, events[(v, v_child, sys_call, id)][0], events[(v, v_child, sys_call, id)][1]) is False:
            return False
    return True

def backward_check(e_, e, u, parents, events):
    lower_limit = min(events[e_][1], events[e][1])
    upper_limit = max(events[e_][1], events[e][1])
    for parent in generate_parents(u, parents):
        u_parent = parent[0]
        sys_call = parent[1]
        id = parent[2]
        if check_overlap(lower_limit, upper_limit, events[(u_parent, u, sys_call, id)][0], events[(u_parent, u, sys_call, id)][1]) is False:
            # print "False Returned-Backward"
            return False
    return True

def merge(e_, e, events):
    lower_limit = min(events[e_][0], events[e][0])
    upper_limit = max(events[e_][1], events[e][1])

    print "Please Merge --", e_, " and ", e, "\n"
    print "with upper limit as %.04f" % upper_limit
    print "with lower limit as %.04f" % lower_limit

    return lower_limit, upper_limit

def make_final_csv(events_final):
    with open('reduced_output.csv', mode='w') as f:
        employee_writer = csv.writer(f, delimiter=',')
        for k, value in events_final.items():
            k_list = list(k)
            value_list = list(value)
            l = k_list + value_list
            employee_writer.writerow(l)

def reduction():
    parents, children, events = parser()
    print events
    stacks = defaultdict(list)
    # parents[v].append((u, sys_call, id))
    # children[u].append((v, sys_call, id))
    # events[(u, v, sys_call, id)] = (time_start, time_start)

    events = OrderedDict(sorted(events.items(), key = lambda (k, v): v[0]))
    events_final = events
    # print events.values()
    for event, time_interval in events.items():
        u, v, sys_call, _ = event
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
                del events_final[event]
                stacks[(u, v, sys_call)].append(candidate_event)
            else:
                stacks[(u, v, sys_call)].append(event)

    make_final_csv(events_final)



def main():
    reduction()


if __name__ == '__main__':
    main()
