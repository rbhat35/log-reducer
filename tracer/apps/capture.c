#include <linux/hw_breakpoint.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <asm/unistd.h>
#include <errno.h>

#include<intel-pt.h>
#include "perf-stream.h"
#include "pt-decoder.h"

int main(int argc, char **argv) 
{
    /* Setup perf to stream PT events. */
    int fd, rc;
    int error = 0;
    pid_t pid;

    if (argc < 2) {
        fprintf(stderr, "Usage %s pid\n", argv[0]);
        exit(1);
    } else {
        pid = (pid_t) atoi(argv[1]);
    }

    // Init perf and setup pt data stream.
    init_perf();
    fd = perf_event_open(pid);
    perf_map(fd, AUX_PAGES, DATA_PAGES);

    init_libipt();
    init_pkt_decoder();

    while(error = pt_pkt_sync_forward(decoder)) {
        sleep(1);
        DEBUG("Waiting for data.\n");
    }

    struct pt_packet *pkt;
    while(pkt = get_next_packet(decoder)) {
        if (pkt)
            free(pkt);
    }
    pt_pkt_free_decoder(decoder);
}
