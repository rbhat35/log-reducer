### libipt Instruction Flow Layer

The instruction flow layer provides a simple API for iterative over 
instructions in execution order.  


#### The Traced Image

The instruction layer needs additional information besides the packet
information. The memory image is reprsentation by a `pt_image`. An image
is a collection of contiguous, non-overlapping memory regions called `sections`.

To create a new pt image, repeated calls to `pt_image_add_file()` will add
all sections from another image. 

#### Intel sideband 

A sideband tracing session serves one Intel PT decoder. 


* primary sideband channels - affect decode directly

** They actively change the Intel PT decoder's image on context switch sideband recoreds.

* Secondary sideband channels affect decode indirectly.

** They maintain the memory iamge for different process contexts but do not actively switch the 
   Intel PT decoder's memory image. 


#### Sideband API

Sideband decoding is defined in the context of a session, which maintains context related to the
current stream being parsed. Internally, the sideband library maintains a session using the 
`struct pt_sb_session`. The session struct holds references to the following information


* contexts -- A list of contexts that ..  

__Sideband Decoding Sessions__:

When decoding sideband information, sessions information related to the decoders, caches, and contexts
used in the session are maintined in a `struct pt_sb_session`. The main information stored in a session
is the image cache, decoders used, and a list of contexts related to the processes that were or are being
traced. 

__Decoder States__:

Next, the session maintains four lists of decoders. The list that a decoder belongs to is based 
on which state the decoder is in: waiting, retired, removed, and "decoders". 

* waiting - A list of newly added sideband decoders. 
* decoders - A list of sideband decoders ordered by their tsc (ascending).
* retired - A list of retired sideband decoders in no particular order. Decoders in the retired list have 
  ran out of trace, but might still have postponed effects pending. 
* removed - A list of removed sideband decoders that are waiting for destruction.  
* decoders -- A list of decoders ordered by their tsc in ascending order. 

The remaining major fields for the session data structure are related to callbacks, which can be registered
when an error occurs or during context switches. 


__Sideband Process Contexts__

During a pt trace, it is likely that data from multiple processes will be involed in the trace. Therefore, 
it is necessaryu to maintain context related to each process. For sideband information, the data structure 
`struct pt_sb_context` is used to maintain context related to each process that was involved in the tracing.
The contexts are maintainted through out the section, and a list of contexts during a session can be found in 
the session's `contexts` list.

__Process Image__

When decoding intel-pt data in some cases the packet data is not enough to create higher-level represenations
of the traced information. For example, if we want to reconstruct the execution flow then we need information
related to the actual code pages that were executed, so that we can create a memory image for the process. 
This is where the process image comes into play. During a tracing session, we need to maintain copies of 
executed code pages, which is capable through perf when it is set to track when pages are marked as executable. 
These pages are streamed through the sideband, and the process context contains a `struct pt_image *image`. We
discuss how the process image is created in more detail later.

__Context API__

The final part of the context is the API used to maintain the context of a process. The code for the 
most interesting is below, which essentially be described as a manager function for maintain the state 
of the processes images. Note, when describing a processes image we are specifcially talking only about the
pages that are marked executable. 

Additionally, one reason the sideband information must maintain a session is due this image being dynamic. This
is especially true when JIT compilation or interpretation is being used. Since we are leveraging a dynamic 
approach to maintaining the image then we can accurately create decoded the instructions. The function has the 
following responsibilities:


```C
int pt_sb_ctx_mmap(struct pt_sb_session *session, struct pt_sb_context *context,
    const char *filename, uint64_t offset, uint64_t size, uint64_t vaddr)
{
    struct pt_image_section_cache *iscache;
    struct pt_image *image;
    int isid;

    image = pt_sb_ctx_image(context);
    if (!image)
        return -pte_internal;

    iscache = pt_sb_iscache(session);
    if (!iscache)
        return pt_image_add_file(image, filename, offset, size, NULL, vaddr);

    isid = pt_iscache_add_file(iscache, filename, offset, size, vaddr);
    if (isid < 0)
        return isid;

    return pt_image_add_cached(image, iscache, isid, NULL);
}
```

__Sideband Decoder__:

The decoder, which despite its name does not do a lot of decoding itself. Internally, this is maintained by the code in the file related to 
sideband events `pt_sb_pevet.c`. Instead, the decoder data structure, which is defined as `struct pt_sb_decoder`, create a template-like 
structure, which requires callbacks to be registered for fetching sideband recoreds and applying sideband records. The default definitions
for these functions are defined in sb\_events. This makes the code mode extensible. 


__Sideband Events API__:

The final module found in Intel's libpt-sb library is the `sb_event` module. This module is where all the heavy-lifting for parsing records
in the perf stream is located. Due to this, we will just discuss the high-level details of this module. 

### Creating a decoder:

In order to create a new decoder, the function `pt_sb_alloc_pevent_decoder(session, config)` is used, which is defined in the event API.
The parameters of this API are the session to assign this decoder, and a configuration, which describe the functionality of this decoder. 

It registers three callback functions for the decoder. 

1. fetch - `pt_sb_pevent_fetch_callback`
2. apply - `pt_sb_pevent_apply_callback`
3. print - `pt_sb_pevent_print_callback`
4.  dtor  `pt_sb_pevent_dtor`

Finrally,, this function simply creates a private version of the pevent and configures it based on the configuration passed in by the 
user. Next, it calls `pt_sb_alloc_decoder(session, config)`. The cavest is that config is redefined using a private version.

### `pt_sb_pevent_priv`

The `pt_sb_pevent_priv` data structure is an internal structure that maintains the start of parsing the perf stream. It main fields 
are the following:

1. filename -- The filename containing the perf data.
2. begin, end -- The beginning and ending of where the perf data was mapped into memory from.
3. curren,next -- The current position in the buffer and the next position from which to fetch.
4. event -- The curent perf event `struct pev_event` record
5. context, next\_context - The current and next process's context



### `pt_sb_pevent_fetch_callback`

The fetch callback is responsible for fetching new records from the perf stream, and warps the `pt_sb_pevent_fetch` function, which is
what will be discussed in this section. This approach has the following capability:

1. The first step in this function is to simply call `pev_read`, which is a part of the pevent module, and this module maintain parsing raw
perf data. Therefore, we will just assume, when pev\_read is called it returns the next `struct pev_event` in perf's data stream.
2. It needs to update the next pointer to `pos + size`, where size is the number of bytes read from pev read.

### `pt_sb_pevent_apply`

1. Apply all our sideband records one-by-one until we're in sync with the event. 

#### `pt_sb_pevent_apply_event_record`

This function acts as a dispatcher to determine which perf event is needs to be parsed. It only considers the following events:

__Fork Events__:
* If we are not creating a new thread, the first task is to create a new context for this process. This will create a new context,
and store it in the session data structure.

* Next, we need to verify that we have a valid image for both the parent and the child, and if so we initialize the child's image
with the parent's image.

__Exec Events__:

* When an exec occurs, we need to create a new context and a new image. There reason we create a new context instead of just 
deleting the old image is because we may still be using the old image. 


__Itrace Start__:

This event occurs when a new instruction begins. In this case, we call `prepare_switch_to_pid`, which setups a switch to the current
pid's context.

__MMAP Events__:

MMAP events, which are events that contain executable pages require the most work, since we need to update the image cache. 




__SideBand Decoding Workflow__:

1. The first step of the decoding sideband information is buildling the session, which will maintain the high-level management 
of parsing the session data. Creating a session is straight forward. A call to `pt_sb_alloc` will return a new session. In the next
steps we will begin setting up the decoders that will do most of the heavy lifting in the session. 

2. Next, we need to create a new decoder, which will be saved to this session. This is completed by calling `pt_sb_alloc_pevent_decoder`.
One issue we need to modify is the call to `pt_sb_pevent_init`. This is because during this call, there is a call to `pt_sb_file_load`. 
In this case, it is assuming the sideband information is already stored in a file. However, this is not the case for us, since we are 
working with a live aux region. Actually, `pt_sb_file_load` only task is to load in the data from the file and save to a buffer, which
will eventually be the buffer in which the parsing is completed. Once the decoder we are technically ready to start decoding sideband information.

3. To decoder sideband information, we need to leverage the fetch, apply functions. 



Fetching and Applying Sideband Events
===


__Fetching__:
The sideband decoder internally maintains a private data structure called `struct pt_sb_pevent_priv *priv`, which is responsible
for maintaining the state of the decoding of the internal perf data. It's primary fields are the 

* current, next -- These are the current position in the stream in the next position in the stream.
* context, `next_context` - This is the context of the current process
* event -- This is the current perf event.
* location - The current code location estimated from prevous events. 


Sideband events are fetched from the aux band using `pt_sb_pevent_fetch`, which internally calls `pev_read()`.  When a fetch is 
called, priv data structure is updated such that the fetched event becomes the current event.

__Applyying__:

The apply process is more involved then fetching. The input paramers to apply are the following:

1. The decoding session.
2. A pointer to a pt\_image.
3. The event to be applied to the decoders.
4. A reference to the priv data structure.


__Initial fetch call.__

The first check is to check if the last record fetched occured prior to the event passed as parameter 3. If this is true, 
then we need to maintain the correct sequential order. In order to achieve this, we apply the current record prior to the
event record. Additionally, we verify this is not the last record. 

```C
    record = &priv->event;
    if ((priv->current != priv->next) &&
            (!record->sample.time || (record->sample.tsc <= event->tsc)))
                    return pt_sb_pevent_apply_event_record(session, image, priv,
                    record);
```                    

__Applying the Event Record__:

When an event record is applied, `pt_sb_pevent_apply_event_record` is called with the same parameters as the original 
fetch call. However, this call does not do any of the sequential checking that occurs in the public fetch call. It 
simply uses a large dispatcher, and choose the decoder based on what the perf record type is. We described what occurs
based on which type of record is being decoded below.



__PERF\_ITRACE\_START__:

This record type will essentially always be the first record in the sideband. When this record occurs, `pt_sb_pevent_itrace_start`
will be called. Overall, this function is simply a wrapper function that updates the `priv` dat structure and  We described what occurs
based on which type of record is being decoded below. Additionally it has two additional steps, which prepare for a context switch to
the pid that created the record, which essentially sets the correct context in  `priv`.


__PERF\_RECORD\_COMM (exec):__

On exec record, we do the following:

1. Create a new image that will ahve kernel sections initialized, but will otherwise be empty. The image will get populated
   using map records later on. 
   2. Next, We setup a switch to the next context. 


__MMAP Records__:

When a mmap record occurs, this is where the image is created. 




1. We check what type of file is being mapped in based on the file name.

2. We call `pt_sb_ctx_mmap`, which is what will maintain the image under this context. First, this function gets the image
for the curent context. Next, assuming we are not using a image cache, `pt_image_add_file` is called, which is defined in `pt_image.c`,
which will add it to the image data structure for this process. 




