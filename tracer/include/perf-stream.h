#ifndef __PERF_STREAM_H__
#define __PERF_STREAM_H__

#include <linux/perf_event.h>
#include "common.h"

// The Intel PT PMU type is dynamic. and its value can be extracted from
// sys/bus/event_source/devices/intel_pt/type
#define PT_PMU_TYPE 6
/** Do not trace kernel events if set to 1.
* This value will be set in perf_event_attr structure:
* http://man7.org/linux/man-pages/man2/perf_event_open.2.html
*/
#define EXCLUDE_KERNEL 1

/* Global variables used by perf. 
 *
 * attr - Maintains the perf configuration. Calling init_perf() will 
 * initialize attr.
 *
 * header - A pointer to the beginning of the perf memory regions. This
 * is equivalent to the base pointer described below.
 *
 * */
struct perf_event_attr attr;
struct perf_event_mmap_page *header;

/* Pointers to memory regions used by perf.
 *
 * base - The beginning of the page mapped in to maintain the perf
 * configuration and metadat.
 * data - The beginning of the perf data section
 * aux - The beginning of the perf aux section.
 */
void *base, *data, *aux;

/** Getters for information related to aux section.
 * 
 */
void *get_aux_begin();
void *get_aux_end();
void *get_data_begin();
void *get_data_end();

/** Init the perf_event_attr structure.
 *
 * Configures the perf_event_attr structure to handle intel-pt data.
 */
int init_perf();

/* perf_event_open 
 Wrapper around perf_event_open syscall.
 *
 * @pid - The pid of the process we are tracing.
 *
 * Returns - Returns the fd that corresponds to the intel pt events
 * if call is successful. Otherwise, call will bail and exit.
 *
 * TODO: Setup approach to make process wait until we are attached.
 */
int perf_event_open(pid_t pid); 

/**Define the sizes of the aux and data memory regons. 
 *
 * 2^AUX_PAGES are mapped in for the aux section.
 * 2^DATA_PAGES are mapped in for the aux section. 
 */
#define AUX_PAGES 4
#define DATA_PAGES 4

/** Create memory for AUX, DATA, and perf_event_mmap page.
 *
 * AUX section - The AUX area is a channel appropraite for high bandwidth
 * datastreams, which is where the intel-pt data stream is stored. 
 * DATA section - For intel-pt the data section contains sideband information
 * that is necessary for decoding the trace.
 *
 * Input:
 *   \@fd - The fd that corresponds to the intel-pt events. This will be the
 *   fd returned from perf_event_open.
 *   \@data_n - The size of the auxilary section 
 *   \@aux_n - The size of the data section 
 *   -- aux and data sections (must be a power of 2 number of pages).
 *
 *   e.g. to create a aux data section with two pages, set aux_n = 1.
 */
void perf_map(int fd, size_t data_n, size_t aux_n);
#endif
