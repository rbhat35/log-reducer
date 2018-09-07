#include "pt-decoder.h"
#include <intel-pt.h>
#include <libipt-sb.h>
#include "perf-stream.h"

void init_sb_decoder() {

    struct pt_sb_pevent_config sb_config;
    struct pt_sb_session *sb_session = NULL;
    int error = NULL;
    memset(&sb_config, 0, sizeof(sb_config));

    // Configure perf sb config.
    sb_config.size = sizeof(sb_config);
    sb_config.filename = "sb.data";
    sb_config.begin = get_data_begin();
    sb_config.time_shift = header->time_shift;
    sb_config.time_mult = header->time_mult;
    sb_config.time_zero = header->time_zero;
    //sb_config.sample_type = header->sample_type;
    // Create a new pt sb session.
    sb_session = pt_sb_alloc(NULL);
    if(!sb_session)
        fail("Failed to create sideband session\n.");

    // Create pevent_decoder.
    error = pt_sb_alloc_pevent_decoder(sb_session, &sb_config);
    if (error) {
        T_DEBUG("ptse_trace_lost: %d\n", pte_invalid);
        fail("Failed to allocate sb decoder (err: %d)\n", error);
    }
}

struct pt_packet* pt_packet_new() {
    struct pt_packet *pkt = NULL;

    pkt = malloc(sizeof(struct pt_packet));
    memset(pkt, 0, sizeof(struct pt_packet));
    return pkt;
}


void init_libipt() {
    memset(&config, 0, sizeof(config));
    config.size = sizeof(config);
    //XXX. Add check to verify aux section has been set.  
    // Set beginning and end to aux region mapped in by perf.
    config.begin = get_aux_begin();
    config.end = get_aux_end();
}

void init_pkt_decoder() {
    decoder = pt_pkt_alloc_decoder(&config);

    if(!decoder) {
        fail("Failed to initialize packet decoder.\n");
    }

    T_DEBUG("Packet decoder initialized.\n");
}


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
    T_DEBUG("pkt type: %d --> %s\n", pkt->type, pkt_name);
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
