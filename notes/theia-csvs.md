backward-edge-0.csv
===

Column0 -- RecordType
Column1 -- HostUUID-EventUUID
Column2 -- EventType 
Column3 -- HostUUID-ProcessUUID 
Column4 -- HostUUID-ResourceUUID 
Column5 -- HostUUID-ResourceUUID2 
Column6 -- timestamp 
Column8 -- size 

Notes:

* The ResourceUUID2 can be ignored. 
* The size value represents the number of bytes read or written to by the syscall. When a merge of read or write syscalls occurs, 
  the size will need to equal the sum of all the merged reads/writes.

Event\_Types:

read, recv, recvmsg


forward-edge-\*.csv
===

The format is the same as backward-edge.csv files.

EventTypes to reduce:

write, sendto, sendmsg

Notes:

* Any eventTypes included in the csv files but are not events that need to be
  reduced can be directly copied over to the output csv file. 
* This would be a nice place to drop most MMAP calls, but we can do this later. 

subject-nodes-\*.csv
===

Represent processes that were executed during the logging.

Column0 -- RecordType
Column1 -- HostUUID-SubjectUUID
Column2 -- SubjectType 
Column3 -- PID
Column4 -- HostUUID-ParentSubjectUUID 
Column5 -- HostUUID-PrincipalUUID
Column6 -- Timestamp
Column7 -- commandLine
Column8 -- pathname

netflow-nodes-\*.csv
===

Represents a internet (INET socket) connection between the system and an IP

Column0 -- RecordType
Column1 -- HostUUID-NetflowUUID (unique id)
Column2 -- Local IP address
Column3 -- Local port
Column4 -- RemoteAddress
Column5 -- RemotePort
Column6 -- name

file-node-\*.csv
===

Represents a file node.


Column0 -- RecordType
Column1 -- HostUUID-FileUUID
Column2 -- HostUUID-PrincipalUUID
Column3 -- filename
Column4 -- name


ipc-node-\*.csv
===

Represents a IPC channel (ignore for now).

Column0 -- RecordType
Column1 -- HostUUID-IPCUUID (unique id)
Column2 -- Local IP address
Column3 -- Local port
Column4 -- RemoteAddress
Column5 -- RemotePort
Column6 -- name
