import time
from parser import compareTo


def timed(decorated_fn):
    def wrapper_fn(*args, **kwargs):
        s = time.time()
        retval = decorated_fn(*args, **kwargs)
        e = time.time()
        print decorated_fn, "took", (e-s), "seconds"
        return retval

    return wrapper_fn

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
    if start_1 > start_2:
        temp = start_2
        start_2 = start_1
        start_1 = temp

        temp = end_2
        end_2 = end_1
        end_1 = temp

    if start_2 <= end_1 or end_2 <= end_1:
        return True

    return False


@timed
def forward_check(e_, e, v, children, events):
    lower_limit = events[e][0]
    upper_limit = events[e_][0]

    if compareTo(events[e_][0], events[e][0]):
        lower_limit = events[e_][0]
        upper_limit = events[e][0]

    for child in generate_children(v, children):
        v_child = child[0]
        sys_call = child[1]
        id = child[2]
        if check_overlap(lower_limit, upper_limit, events[(v, v_child, sys_call, id)][0], events[(v, v_child, sys_call, id)][1]):
            return False
    return True


@timed
def backward_check(e_, e, u, parents, events):
    lower_limit = events[e][1]
    upper_limit = events[e_][1]

    if compareTo(events[e_][1], events[e][1]):
        lower_limit = events[e_][1]
        upper_limit = events[e][1]

    for parent in generate_parents(u, parents):
        u_parent = parent[0]
        sys_call = parent[1]
        id = parent[2]
        if check_overlap(lower_limit, upper_limit, events[(u_parent, u, sys_call, id)][0], events[(u_parent, u, sys_call, id)][1]):
            # print "False Returned-Backward"
            return False
    return True
