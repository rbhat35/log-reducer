#ifdef __SB_H__
#define __SB_H__

#include "common.h"
#include "pevent.h"
#include <intel-pt>

int init_perf_pv();
struct pev_event *read_data_pv();

#endif
