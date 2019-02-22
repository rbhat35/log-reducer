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
def make_final_csv(events_final, csv_details, sizes, count):
    forward_count = 0
    backward_count = 0

    forward_file_index = 0
    backward_file_index = 0

    forward_file_name = str(count) + 'forward-reduced-%05d.csv'
    backward_file_name = str(count) + 'backward-reduced-%05d.csv'

    forward_file = open(forward_file_name % forward_file_index, mode='w')
    backward_file = open(backward_file_name % backward_file_index, mode='w')

    forward_writer = csv.writer(forward_file, delimiter=',')
    backward_writer = csv.writer(backward_file, delimiter=',')

    num_entries_per_file = 10000

    for k, value in events_final.items():
        u, v, sys_call, id = k
        zero_col, one_col, five_col, six_col, eight_col, tag = csv_details[id]
        time_start, time_end = value
        size = sizes[id]

        if size == 0:
            size = ""

        if tag == 'FORWARD':
            forward_count += 1
            l = [zero_col, one_col, sys_call, v, u, five_col, six_col, size, eight_col, time_start, time_end]
            forward_writer.writerow(l)
        elif tag == 'BACKWARD':
            backward_count += 1
            l = [zero_col, one_col, sys_call, u, v, five_col, six_col, size, eight_col, time_start, time_end]
            backward_writer.writerow(l)

        if forward_count % num_entries_per_file == 0:
            forward_file.flush()
            forward_file.close()

            forward_file_index += 1
            forward_file = open(forward_file_name % forward_file_index, mode='w')
            forward_writer = csv.writer(forward_file, delimiter=',')

        if backward_count % num_entries_per_file == 0:
            backward_file.flush()
            backward_file.close()

            backward_file_index += 1
            backward_file = open(backward_file_name % backward_file_index, mode='w')
            backward_writer = csv.writer(backward_file, delimiter=',')

    forward_file.close()
    backward_file.close()

    print "forward count --> ", forward_count
    print "backward count --> ", backward_count
