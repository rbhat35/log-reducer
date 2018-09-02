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

//struct pev_config p_config;


struct perf_event_mmap_page *header;

struct pt_config config;


char * pkt_type_to_str(enum pt_packet_type type);


/* Initialize a new pt packet.
 *
 */
struct pt_packet* pt_packet_new() {
    struct pt_packet *pkt = NULL;

    pkt = malloc(sizeof(struct pt_packet));
    memset(pkt, 0, sizeof(struct pt_packet));
    return pkt;
}

/** Get the next pt packet .
 *
 * Returns the next pt packet if success. O.W. NULL
 */
struct pt_packet* get_next_packet(struct pt_packet_decoder *decoder)
{
    int error = 0;
    struct pt_packet *pkt = NULL;
    
    pkt = pt_packet_new();
    error = pt_pkt_next(decoder, pkt, sizeof(struct pt_packet));
    if (error < 0) {
        DEBUG("Failed to get next packet (%d).\n", error);
        free(pkt);
        pkt = NULL;
        return NULL;
    }

#ifdef CONFIG_DEBUG
    char * pkt_name = pkt_type_to_str(pkt->type);
    DEBUG("pkt type: %d --> %s\n", pkt->type, pkt_name);
#endif

    return pkt;
}

/* 
 * Type map:
 * https://stackoverflow.com/questions/18070763/get-enum-value-by-name
 */
char *pkt_type_to_str(enum pt_packet_type type)
{
    const struct {
        char *name;
        enum pt_packet_type type;
    } typemap[] = {
#define Type(x) {#x, x}
        Type(ppt_pad),
        Type(ppt_psb),
        Type(ppt_psbend),
        Type(ppt_fup),
        Type(ppt_tip),
        Type(ppt_tip_pge),
        Type(ppt_tip_pgd),
        Type(ppt_tnt_8),
        Type(ppt_tnt_64),
        Type(ppt_mode),
        Type(ppt_pip),
        Type(ppt_vmcs),
        Type(ppt_cbr),
        Type(ppt_tsc),
        Type(ppt_tma),
        Type(ppt_mtc),
        Type(ppt_cyc),
        Type(ppt_stop),
        Type(ppt_ovf),
        Type(ppt_mnt),
        Type(ppt_exstop),
        Type(ppt_mwait),
        Type(ppt_pwre),
        Type(ppt_pwrx),
        Type(ppt_ptw)
#undef Type
    };



    for(size_t i = 0; i < sizeof(typemap) / sizeof(typemap[0]); i++) {
        if (type == typemap[i].type) {
            return typemap[i].name;
        }
    }
    return "Invalid type.";
}


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

    // Setup packet Decoder

    //Configure libipt.
//    memset(&config, 0, sizeof(config));
//    config.size = sizeof(config);
//    config.begin = aux;
//    config.end = aux + header->aux_size;
//
//    // Create packet decoder.
//    struct pt_packet_decoder *decoder;
//    decoder = pt_pkt_alloc_decoder(&config);
//    if(!decoder) {
//        DEBUG("decoder init error\n");
//        fail();
//    }
//  
//    // Wait until we get data.
//    while(error = pt_pkt_sync_forward(decoder)) {
//        sleep(1);
//        DEBUG("Waiting for data.\n");
//    }
//    // Get packets.
//    struct pt_packet *pkt;
//    while(pkt = get_next_packet(decoder)) {
//        if (pkt)
//            free(pkt);
//    }
//
//    // Cleanup.
//    pt_pkt_free_decoder(decoder);
}
