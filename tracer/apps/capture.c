#include <linux/hw_breakpoint.h>
#include <unistd.h>
#include <sys/wait.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <asm/unistd.h>
#include <errno.h>
#include <fcntl.h>

#include <intel-pt.h>
#include "perf-stream.h"
#include "pt-decoder.h"
#include "sb.h"

int main(int argc, char **argv) 
{
    /* Setup perf to stream PT events. */
	int fds[2];
    char buf[2];
    int fd, rc;
    int error = 0;
    pid_t pid;

    if (argc < 2) {
        fprintf(stderr, "Usage %s pid\n", argv[0]);
        exit(1);
    }

    /* Setup tracing process. */
	if (pipe(fds) != 0) {
		fprintf(stderr, "Error creating pipe.\n");
		return 1;
	}

    /* Create child process to trace and have it wait for 
     * parent before running exec. 
     */
    switch ((pid=fork())) {

        case -1:
            fprintf(stderr, "Error Forking\n");
            return 1;
        case 0: /* Child */
			printf("Waiting to execute: %s\n", argv[1]);
			close(fds[1]);
			while (read(fds[0], buf, 1) == -1 && errno == EINTR)
				/* blank */ ;
			fprintf(stderr, "exec: %s\n", argv[1]);
			close(fds[0]);
			execvp(argv[1], &argv[1]);
			fprintf(stderr, "Failed to exec %s\n", argv[1]);
			return 1;
        default: /* parent */
			close(fds[0]);
			fcntl(fds[1], F_SETFD, FD_CLOEXEC);

            /* Setup tracing for parent. */
            init_perf();
            fd = perf_event_open(pid);
            perf_map(fd, AUX_PAGES, DATA_PAGES);
            init_libipt();
            init_pkt_decoder();

           
            // Start child exec.
			if (write(fds[1],"1", 1) != 1) {
				kill(pid,SIGTERM);
				//(void)delete_all_rules(audit_fd);
				exit(1);
			}

            waitpid(pid, NULL, 0);
            close(fds[1]);

            while(error = pt_pkt_sync_forward(decoder)) {
                sleep(1);
                DEBUG("Waiting for data. (%d)\n", error);
            }
            
            init_perf_pv();
            init_sb_decoding();
            fetch_event();

            /* Read perf data. */
            //while (1)
            //    read_data_pv();
    }

    pt_pkt_free_decoder(decoder);
}
