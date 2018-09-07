#include "sb.h"
#include <stdio.h>
#include "pevent.h"
#include "perf-stream.h"

struct pev_config pv_config;

uint8_t *stream = NULL;

int init_perf_pv() {

    pev_config_init(&pv_config);

    pv_config.time_shift = header->time_shift;
    pv_config.time_mult = header->time_mult;
    pv_config.time_zero = header->time_zero;
}

struct pev_event *read_data_pv() {
    struct pev_event *event = NULL;
    int rc = 0;

    if (!stream) {
        stream = get_data_begin();
    }

    event = malloc(sizeof(struct pev_event));
    
    rc = pev_read(event, stream, get_data_end(), &pv_config);
    if (rc < 0) {
        fail("Failed to read perf event. rc(%d)\n", rc);
    } else {
        T_DEBUG("perf event size: rc(%d)\n", rc);
        stream += rc;
    }

    printf("pev_event %u\n", event->type);
    fflush(stdout);

    return event;
}
