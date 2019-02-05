Input: E = list of ([start, end] for each system call)
tw: time interval #Implementation is designer's choice
ts: start time #Implementation is designer's choice
te: end time #Implementation is designer's choice


PARSE(E):
    parent = defaultdict(list)
    children = defaultdict(list)
    for e in E:
        u = src(e)
        v = dest(e)
        parent[v].append(u)
        children[u].append(v)

    return parent, children

CPR_AGGREGATE(E):
    parent, children = PARSE(E) #Probably don't need a separate PARSE, but still thinking about it
    for e in E:
        u = src(e)
        v = dest(v)
        # every type of system call has its own stack for a source and destination.
        # Let S be the stack specific to that system call and u, v

        if S is empty:
            S.push(e)
        else:
            e_ = S.pop()
            if (FORWARD_CHECK(e_, e, v, children) and BACKWARD_CHECK(e_, e, u, parent)):
                e_ = MERGE(e_, e)
                S.push(e_)
            else:
                S.push(e)

FORWARD_CHECK(e_, e, v, children):
    outgoing = children[v]

    for e in outgoing:
        if tw[e] overlaps with [ts[e_], ts[e]]:
            return False

    return True

BACKWARD_CHECK(e_, e, u, parent):
    incoming = parent[u]

    for e in incoming:
        if tw[e] overlaps with [te[e_], te[e]]:
            return False

    return True

MERGE(e_, e):
    end_time = max(te[e_], te[e]) #Algorithm in the paper assumes te[e] > te[e_]. Not sure why?
    start_time = ts[e_] #popped egde (chronological order)
    common_id = average(id(e_), id(e))
    new_e = (common_id, start_time, end_time)
    DELETE(e)
    return e_
