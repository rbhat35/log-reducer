import sys
import time

from linux_audit_reduction import reduction as linux_reduction
from theia_reduction import reduction as theia_reduction

incoming_dir = sys.argv[1]

INCOMING_DIR = incoming_dir


def main():
    global_list_processed_files_forward = set()
    global_list_processed_files_backward = set()
    count = 0
    if "is_theia" in sys.argv:
        reduction_code = theia_reduction
    else:
        reduction_code = linux_reduction

    while (1):
        global_list_processed_files_forward, \
            global_list_processed_files_backward = reduction_code(global_list_processed_files_forward, \
                global_list_processed_files_backward, count, incoming_dir)
        count += 1
        time.sleep(15)


if __name__ == '__main__':
    main()
