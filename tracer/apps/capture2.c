#include <linux/perf_event.h>
#include <poll.h>
#include <linux/hw_breakpoint.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <asm/unistd.h>
#include <errno.h>

#include "pevent.h"

struct perf_event_attr attr;

struct perf_event_mmap_page *header;
void *base, *data, *aux;

/*
 * Inits the perf_event_attr structure.
 */
int init_perf()
{

    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.type = 6;
    attr.exclude_kernel = 1;
    //attr.sample_period = 1;
    //attr.disabled = 1;

    // The Intel PT PMU type is dynamic. and its value can be extracted from
    // sys/bus/event_source/devices/intel_pt/type
}

/*
 * Wrapper around perf_event_open syscall.
 */
int perf_event_open(pid_t pid) 
{
    int fd;
    fd = syscall(__NR_perf_event_open, &attr, pid, -1, -1, 0);
    if (fd < 1) {
        fprintf(stderr, "perf_event_open failed.\n");
        perror(NULL);
        exit(1);
    }

    return fd;
}

/* 
 * mmap in the AUX, DATA, and perf_event_mmap page.
 *
 * AUX section - The AUX area contains the Intel PT trace.
 * DATA section - area contains sideband information such as
 * that are necessary for decoding the trace.
 *
 * Input:
 *   aux_size - The size of the auxilary section 
 *   data_size - The size of the data section 
 *   -- aux and data sections (must be a power of 2 number of pages.
 *    
 */
void perf_map(int fd, size_t data_n, size_t aux_n)
{
    size_t page_size = sysconf(_SC_PAGESIZE);

    // Setup data section.
    size_t data_s = page_size + (2 << data_n)*page_size;
    base = mmap(NULL, data_s, PROT_WRITE, MAP_SHARED, fd, 0);
    if (base == MAP_FAILED) {
        fprintf(stderr, "Failed to mmap base.\n");
        perror(NULL);
        exit(1);
    }

    header = base;
    data = base + header->data_offset;
    header->aux_offset = header->data_offset + header->data_size;

    // Setup aux section.
    header->aux_offset = header->data_offset + header->data_size;
    header->aux_size = (2 << aux_n)*page_size;
    aux = mmap(NULL, header->aux_size, PROT_READ, MAP_SHARED, fd, header->aux_offset);
    if (aux == MAP_FAILED) {
        fprintf(stderr, "Failed to mmap aux.\n");
        perror(NULL);
        exit(1);
    }
}

int main(int argc, char **argv) 
{
    struct perf_event_header eh;
    int fd;
    pid_t pid;
    int rc;

    if (argc < 2) {
        fprintf(stderr, "Usage %s pid\n", argv[0]);
        exit(1);
    } else {
        pid = (pid_t) atoi(argv[1]);
    }


    /* Setup perf to stream PT events. */
    init_perf();
    fd = perf_event_open(pid);
    perf_map(fd, 4, 4);
    
    struct pollfd *p_fd = malloc(sizeof(struct pollfd));
    p_fd->fd = fd;
    p_fd->events = POLLIN;
    int error = 0;

    while (1) {
        sleep(1);
        write(1, aux, 4096);
    }
    //printf("rc: %d\n", rc);


    //rc = memcpy((void*) &eh, header->aux_head, sizeof(struct perf_event_header));
    //if (rc < 0) {
     //   perror(NULL);
    //}
   /* Intel PT trace is saved in AUX area. The DATA area is for sideband info.
     */
}
