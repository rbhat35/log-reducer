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

#include<intel-pt.h>
//#include "pevent.h"
#include "common.h"

//struct pev_config p_config;

struct perf_event_attr attr;

struct perf_event_mmap_page *header;
void *base, *data, *aux;

struct pt_config config;


char * pkt_type_to_str(enum pt_packet_type type);
/*
 * Inits the perf_event_attr structure.
 */
int init_perf()
{

    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.type = 6;
    attr.exclude_kernel = 1;
    attr.sample_id_all = 1;
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
        fail();
    }

    header = base;
    header->data_size = data_s;
    data = base + header->data_offset;
    header->aux_offset = header->data_offset + header->data_size;

    // Setup aux section.
    header->aux_size = (2 << aux_n)*page_size;
    aux = mmap(NULL, header->aux_size, PROT_READ, MAP_SHARED, fd, header->aux_offset);
    if (aux == MAP_FAILED) {
        fprintf(stderr, "Failed to mmap aux.\n");
        fail();
    }
}

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

    for (size_t i = 0; i < sizeof(typemap) / sizeof(typemap[0]); i++) {
        if (type == typemap[i].type) {
            return typemap[i].name;
        }
    }
    return "Invalid type.";
}


int main(int argc, char **argv) 
{
    struct pt_packet_decoder *decoder;
    /* Setup perf to stream PT events. */
    int fd, rc;
    int error = 0;
    pid_t pid;
    struct perf_event_header eh;
    struct pollfd *p_fd = NULL;

    if (argc < 2) {
        fprintf(stderr, "Usage %s pid\n", argv[0]);
        exit(1);
    } else {
        pid = (pid_t) atoi(argv[1]);
    }


    init_perf();
    fd = perf_event_open(pid);
    perf_map(fd, 1, 1);

    memset(&config, 0, sizeof(config));
    config.size = sizeof(config);
    config.begin = aux;
    config.end = aux + header->aux_size;


    decoder = pt_pkt_alloc_decoder(&config);
    if(!decoder) {
        DEBUG("decoder init error\n");
        fail();
    }
  
//    int offset;
//    while (1) {
//        //pt_pkt_decode_unknown(decoder, packet);
//        sleep(1);
//        error = pt_pkt_sync_forward(decoder);
//        if (error) {
//            DEBUG("Failed to sync forward: (%d).\n", error);
//        } else {
//            printf("synced (%d) \n", error);
//            break;
//        }
//        printf("%d\n", offset); 
//        fflush(stdout);
//
//    }

    // Wait until we get data.
    while(error = pt_pkt_sync_forward(decoder)) {
        sleep(1);
        DEBUG("Waiting for data.\n");
    }
    // Get packets.
    struct pt_packet *pkt;
    while(pkt = get_next_packet(decoder));
}
