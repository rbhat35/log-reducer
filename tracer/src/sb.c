#include "sb.h"
#include <stdio.h>
#include "pevent.h"
#include "perf-stream.h"
#include "libipt-sb.h"

struct pev_config pv_config;
struct pt_sb_pevent_config sb_pv_config;
struct pt_sb_decoder_config sb_d_config;

uint8_t *stream = NULL;


int init_sb_decoding() {
    int err = 0;
    struct pt_sb_session *session = NULL;

    // Create a new session. 
    session = pt_sb_alloc(NULL);
    if (!session)
        fail("Failed to initialize session.\n");

    // Intialize decoder configuration.
    memset(&sb_pv_config, 0, sizeof(struct pt_sb_pevent_config));
    sb_pv_config.size = sizeof(struct pt_sb_pevent_config);

    //Allocate a new sideband decoder for this session.
    memset(&sb_pv_config, 0, sizeof(struct pt_sb_pevent_config));
    sb_pv_config.size = sizeof(struct pt_sb_pevent_config);

    err = pt_sb_alloc_pevent_decoder(session, &sb_pv_config, get_data_begin(), header->data_size);
    if (err)
        fail("Failed to initialize sideband decoder (%d).\n", err);

    T_DEBUG("Sideband decoding initialized.\n");
}

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

    FILE * stdout_f = fdopen(1, "r+");
    fflush(stdout);

    return event;
}
