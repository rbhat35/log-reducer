
#include "libipt-sb.h"
#include "pt-decoder.h"
#include "perf-stream.h"
#include "pt_sb_context.h"
#include <stddef.h>
#include "sb.h"

struct pt_insn_decoder;
struct pt_insn_decoder *insn_decoder = NULL;

int handle_events(int status) {

    while (status & pts_event_pending) {
        struct pt_event event;
        status = pt_insn_event(insn_decoder, &event, sizeof(event));

        T_DEBUG("Event status (%d)\n", status);

        if (status < 0)
            break;
    }
}

void print_insns() {
    int err = 0;
    int status = 0;

    for (;;) {

        status = handle_events(1);
        if (status < 0) {
            fail("Status: %d", status);
        }
        struct pt_insn insn;
        memset(&insn, 0, sizeof(insn));

        err = pt_insn_next(insn_decoder, &insn, sizeof(insn));
        if (err) {
            T_DEBUG("Insn err(%d)\n", pte_no_enable);
            fail("Failed to get next instruction. err(%d)\n", err);
        } else { 
            T_DEBUG("Received next instruction! (%d)\n", err);

        }
    }
}

void init_insn_decoder() {
    int err;

    // Create a new insn decoder. 
    insn_decoder = pt_insn_alloc_decoder(&config);
    if(!insn_decoder)
        fail("Failed to create insn decoder.\n");

    T_DEBUG("Instruction decoder initialized.\n");
}

struct pt_insn_decoder *get_insn_decoder(){return insn_decoder;}

/* 
 * For the process with pid  add the image beinging maintained
 * from the sideband session to the instruction decoder.
 */
void add_image_insn(pid_t pid, struct pt_sb_session *session) {
    int err;
    struct pt_sb_context *context = NULL;

    if (!session)
        fail("Session is invalid!\n");

    // Get the context for this pid. 
    context = malloc(sizeof(struct pt_sb_context));
    err = pt_sb_get_context_by_pid(&context, session, pid);
    if (err)
        fail("Failed to get context for pid(%lu): err(%lu)\n", pid, err);

    // Verify the image has been created for this pid.
    struct pt_image * image;
    image = pt_sb_ctx_image(context);
    if(!image)
        fail("The image has not been created for pid (%lu) \n", context->pid);

    err = pt_insn_set_image(insn_decoder, context->image);
    if (err)
        fail("Failed to add image to insn_decoder.\n");

    // Add the image for this process to the instruction decoder.
    pid_t c_pid = context->pid; 
    T_DEBUG("Successfully added image for pid (%lu)(%lu) \n", pid, c_pid);
}


struct pt_packet* pt_packet_new() {
    struct pt_packet *pkt = NULL;

    pkt = malloc(sizeof(struct pt_packet));
    memset(pkt, 0, sizeof(struct pt_packet));
    return pkt;
}


//TODO. This function can probably be internal.
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

    if(!decoder)
        fail("Failed to initialize packet decoder.\n");

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

