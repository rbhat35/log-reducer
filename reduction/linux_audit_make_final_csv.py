import csv
import time


def timed(decorated_fn):
    def wrapper_fn(*args, **kwargs):
        s = time.time()
        retval = decorated_fn(*args, **kwargs)
        e = time.time()
        print decorated_fn, "took", (e-s), "seconds"
        return retval

    return wrapper_fn

@timed
def make_final_csv(events_final, csv_details):
    with open('forward-reduced.csv', mode='w') as f_forward:
        forward_writer = csv.writer(f_forward, delimiter=',')
        with open('backward-reduced.csv', mode='w') as f_backward:
            backward_writer = csv.writer(f_backward, delimiter=',')
            for k, value in events_final.items():
                u, v, sys_call, id = k
                time_start, time_end = value
                first_col = csv_details[id][0]
                fourth_col = csv_details[id][1]
                tag = csv_details[id][2]
                if tag == 'FORWARD':
                    l = [first_col, v, sys_call, fourth_col, u, time_start, time_end]
                    forward_writer.writerow(l)
                elif tag == 'BACKWARD':
                    l = [first_col, u, sys_call, fourth_col, v, time_start, time_end]
                    backward_writer.writerow(l)
