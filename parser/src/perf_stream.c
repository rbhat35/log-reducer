#include <sys/mman.h>
#include <unistd.h>
#include <asm/unistd.h>
#include <stdlib.h>
#include <string.h>

#include "perf-stream.h"

void *get_aux_begin(){return aux;}
void *get_aux_end(){return aux + header->aux_size;}

int init_perf()
{
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.type = PT_PMU_TYPE;
    attr.exclude_kernel = EXCLUDE_KERNEL;
    //XXX. Check if this needs to be set if we are no longer using pevent.c
    attr.sample_id_all = 1;
}


int perf_event_open(pid_t pid) 
{
    int fd;
    fd = syscall(__NR_perf_event_open, &attr, pid, -1, -1, 0);
    if (fd < 1)
        fail("perf_event_open failed.\n");

    return fd;
}


void perf_map(int fd, size_t data_n, size_t aux_n)
{
    size_t page_size, data_s, aux_s;
        
    page_size = sysconf(_SC_PAGESIZE);
    data_s = page_size + (2 << data_n)*page_size;
    aux_s = (2 << aux_n)*page_size;

    // Create data region.
    base = mmap(NULL, data_s, PROT_WRITE, MAP_SHARED, fd, 0);
    if (base == MAP_FAILED)
        fail("Failed to mmap perf base.\n");

    // Setup perf header page and store info related to data and aux region.
    header = base;
    header->data_size = data_s;
    data = base + header->data_offset;
    header->aux_offset = header->data_offset + header->data_size;
    header->aux_size = aux_s;

    // Create aux region.
    aux = mmap(NULL, aux_s, PROT_READ, MAP_SHARED, fd, header->aux_offset);
    if (aux == MAP_FAILED)
        fail("Failed to mmap perf aux section.\n");

    T_DEBUG("Aux and Data sections initialized.\n");
}
