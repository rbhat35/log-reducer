#include "sb.h"
#include <stdio.h>
#include "pevent.h"
#include "perf-stream.h"
#include "libipt-sb.h"


uint8_t *stream_sb = NULL;
struct pt_sb_session *session = NULL;


struct pt_sb_session *get_session(){return session;}

//int get_image(pid_t) {
//    return -1;
//}

int init_sb_decoding() {
    int err = 0;
    uint8_t* data = NULL;
    size_t size = 0;

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
    data = get_data_begin();
    size = header->data_size;
    err = pt_sb_alloc_pevent_decoder(session, &sb_pv_config, data, size);
    if (err)
        fail("Failed to initialize sideband decoder (%d).\n", err);

    T_DEBUG("Sideband decoding initialized.\n");
}

int fetch_event() {
    int err = 0;
    /* Initalize decoders. */
    err = pt_sb_init_decoders(session);
    if (err)
        fail("Failed to initialize decoders.\n");
    T_DEBUG("Fetching Event!\n");

    sb_d_config.fetch(session, -1, sb_d_config.priv);
}

int print_event() {
    int err = 0;
    char *filename = "test.dump";

    /* Initalize decoders. */
    err = pt_sb_init_decoders(session);
    if (err)
        fail("Failed to initialize decoders.\n");

    FILE* f_out = fopen(filename, "w");
    T_DEBUG("Fetching all records.");
    err = pt_sb_dump(session, f_out, ptsbp_tsc | ptsbp_verbose, -1);
    if (err) {
        fail("Failed to dump sideband records.");
    } else {
        T_DEBUG("Finished fetching.\n");
    }

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

    if (!stream_sb) {
        stream_sb = get_data_begin();
    }

    event = malloc(sizeof(struct pev_event));
    rc = pev_read(event, stream_sb, get_data_end(), &pv_config);

    if (rc < 0) {
        fail("Failed to read perf event. rc(%d)\n", rc);
    } else {
        T_DEBUG("perf event size: rc(%d)\n", rc);
        stream_sb += rc;
    }

    FILE * stdout_f = fdopen(1, "r+");
    fflush(stdout);

    return event;
}
