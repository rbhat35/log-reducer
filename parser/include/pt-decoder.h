#ifndef __PT_PKT_DECODER_H__
#define __PT_PKT_DECODER_H__

#include <intel-pt.h>
#include "common.h"

/** libipt configuration options.
 * 
 * Holds the configuration parameters for libipt. A call 
 * to init_libipt will initialize the structure.
 */
struct pt_config config;
/** A pointer to the pkt decoder. 
 *
 *  Initialized by init_pkt_decoder.
 */
struct pt_packet_decoder *decoder;

/* Create a new pt packet.
 *
 * Allocates memory for a new pt packet, and zeroes 
 * out memory. 
 *
 * Returns:
 * -- A pointer to the new pt packet. The pointer should be freed
 *  after use.
 */
struct pt_packet* pt_packet_new();

/** Initializes the configuration parameters used for libipt.
 *
 * This function also configures the linking between the allocated
 * memory regions and the pt buffers used by libipt. Therefore, the
 * call will fail if the perf module has not been initialized yet.
 */
void init_libipt();

/** Initialize the libipt packet decoder. 
 *
 */

void init_pkt_decoder();

/** Get the next pt packet .
 *
 * Returns a pointer to the allocated packet. The caller is responsible
 * for freeing.
 */
struct pt_packet* get_next_packet(struct pt_packet_decoder *decoder);

/** Returns a string representation of the packet type.
 *
 */
char *pkt_type_to_str(enum pt_packet_type type);
#endif
