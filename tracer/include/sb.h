#ifndef __SB_H__
#define __SB_H__

#include "common.h"
#include "pevent.h"
#include "libipt-sb.h"
#include <intel-pt.h>

// Sideband decoding session.

struct pev_config pv_config;
struct pt_sb_pevent_config sb_pv_config;
struct pt_sb_decoder_config sb_d_config;


struct pt_sb_session *get_session();
void add_image_insn(pid_t pid, struct pt_sb_session *session); 
int init_perf_pv();
struct pev_event *read_data_pv();
int fetch_event();
int init_sb_decoding();

int get_image(pid_t pid);

#endif
