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
                zero_col, one_col, five_col, six_col, size, eight_col, tag = csv_details[id]
                time_start, time_end = value
                if size = 0:
                    size = ""
                if tag == 'FORWARD':
                    l = [zero_col, one_col, sys_call, v, u, five_col, six_col, size, eight_col, time_start, time_end]
                    forward_writer.writerow(l)
                elif tag == 'BACKWARD':
                    l = [zero_col, one_col, sys_call, u, v, five_col, six_col, size, eight_col, time_start, time_end]
                    backward_writer.writerow(l)
