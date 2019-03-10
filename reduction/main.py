import sys
import time

from linux_audit_reduction import reduction as linux_reduction

incoming_dir = sys.argv[1]

INCOMING_DIR = incoming_dir


def main():
    global_list_processed_files_forward = set()
    global_list_processed_files_backward = set()
    count = 0

    while (1):
        global_list_processed_files_forward, \
            global_list_processed_files_backward = linux_reduction(global_list_processed_files_forward, \
                global_list_processed_files_backward, count, incoming_dir)
        count += 1
        time.sleep(15)


if __name__ == '__main__':
    main()
