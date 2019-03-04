Tracing Setup
===

The tracing system is built on top of libaudit

```shell
sudo apt-get install python-audit auditd
cd tracer
mkdir bin
make trace
```


Parsing Setup
===

```shell
cd parser
pip install -r requirements.txt
```


Starting Neo4j
===

Start the Neo4j service

```shell
sudo service neo4j start
```

Example Graphs
===

There are two example graphs that can be used to verify the setup is correct
in the examples directory. Run the commands below to create the raw audit
logs. If `run_tests.sh` is ran succesfully, two files will be created:
`readloop_1024.audit` and `readloop_256.audit`.

```shell
cd examples
make
./run_tests.sh
```

The next task is parsing the logs, which will convert the audit format
into csv files that can be inserted into Neo4j. Neo4j is a graph database.
To create the csv files run the commands below, which will create two csv
files `forward.csv` and `backwards.csv`.

```shell
cd parser
python parser.py ../examples/readloop_256.audit
```

```shell
DEBUG:__main__:Parsing syscall: execve
DEBUG:modules.filemap:(27430, 0 = 0)
INFO:modules.filemap:inode: 0
1536767036.242.25336,27430:"/home/jallen309/log-compression-project/examples/readloop",execve,0,"./readloop"
DEBUG:__main__:Parsing syscall: open
DEBUG:modules.filemap:(27430, 3 = 0x1fc0c6a)
INFO:modules.filemap:inode: 0x1fc0c6a
1536767036.262.25337,27430:"/home/jallen309/log-compression-project/examples/readloop",open,0x1fc0c6a,"/etc/ld.so.cache"
DEBUG:__main__:Parsing syscall: close
INFO:modules.filemap:inode: 0x1fc0c6a
1536767036.262.25338,27430:"/home/jallen309/log-compression-project/examples/readloop",close,0x1fc0c6a,"/etc/ld.so.cache"
DEBUG:__main__:Parsing syscall: open
DEBUG:modules.filemap:(27430, 3 = 0x33000a9)
INFO:modules.filemap:inode: 0x33000a9
1536767036.262.25339,27430:"/home/jallen309/log-compression-project/examples/readloop",open,0x33000a9,"/lib/x86_64-linux-gnu/libc.so.6"
DEBUG:__main__:Parsing syscall: read
INFO:modules.filemap:inode: 0x33000a9
1536767036.262.25340,27430:"/home/jallen309/log-compression-project/examples/readloop",read,0x33000a9,"/lib/x86_64-linux-gnu/libc.so.6"
DEBUG:__main__:Parsing syscall: close
INFO:modules.filemap:inode: 0x33000a9
1536767036.262.25341,27430:"/home/jallen309/log-compression-project/examples/readloop",close,0x33000a9,"/lib/x86_64-linux-gnu/libc.so.6"
DEBUG:__main__:Parsing syscall: open
DEBUG:modules.filemap:(27430, 3 = 0xc206d4)
INFO:modules.filemap:inode: 0xc206d4
1536767036.262.25342,27430:"/home/jallen309/log-compression-project/examples/readloop",open,0xc206d4,"256.txt"
DEBUG:__main__:Parsing syscall: read
INFO:modules.filemap:inode: 0xc206d4
1536767036.262.25343,27430:"/home/jallen309/log-compression-project/examples/readloop",read,0xc206d4,"256.txt"
DEBUG:__main__:Parsing syscall: read
INFO:modules.filemap:inode: 0xc206d4
1536767036.262.25344,27430:"/home/jallen309/log-compression-project/examples/readloop",read,0xc206d4,"256.txt"
DEBUG:__main__:Parsing syscall: read
INFO:modules.filemap:inode: 0xc206d4
1536767036.262.25345,27430:"/home/jallen309/log-compression-project/examples/readloop",read,0xc206d4,"256.txt"
```


The final step is to insert the data into Neo4j. To do this run the following
command:

```shell
$ sudo ./neo4j-load-csv.sh .
```

The output should be similar to the following:

```shell
0 rows available after 675 ms, consumed after another 0 ms
Created 2 relationships, Set 4 properties
0 rows available after 1383 ms, consumed after another 0 ms
Created 11 relationships, Set 22 properties
```

Finally, you can view the graph visually by going to http://143.215.130.71:7474/browser/
in a browser. A tutorial on how to visualize the graph can be found here (https://neo4j.com/developer/guide-neo4j-browser/).


Tracing a new Program
===

The trace a program you can run the command `./example.trace.sh "<path to file> <arguments>" output file. For example, to trace the
program `ls` using the command line parameter `-h`, the command below would be used.. The output would be saved to ls.audit.

```shell
./examples/trace.sh "/bin/ls -h" ls.audit
```

Running the reduction code
===
folder_name specifies the folder in which the forward and backward files are present. All the forward
files should be of the form forward-edge-* and all the backward files should be of the form backward-edge-*

```shell
cd reduction
to run the reduction code in theia mode:
python main.py <folder_name> is_theia
to run the reduction code in linux mode:
python main.py <folder_name>

```

Performance Improvement
===
Early versions of our code were taking hours to reduce logs worth just minutes. We were able to drastically improve our runtime by exploiting the fact that logs are sorted chronologically.

In order to check forward and backward dependencies we need to access the parents and children for different nodes (If a directed edge goes from u to v, u is the parent and v is the child).  The information of these parents and children are saved in the form of two adjacency lists. We populate these lists initially at the beginning of the algorithm. For every parent, its children (and their corresponded edges) and for every child, its parents (and their corresponded edges) are saved in the chronological order in these lists.

According to the algorithm, after checking the dependencies, if there is a reduction i.e. two edges need to be replaced by 1, we eliminate the edge from the lists mentioned above. Since each edge has a unique id, we know the id that needs to be deleted (the edge that is redundant according to the reduction algorithm). Here, we use binary search to search the redundant edge id in the lists mentioned above, as opposed to using a linear search being used initially.

This decreased the complexity from O(n) to O(logn) and drastically reduced the reduction time for large logs (for eg. 36 hour logs).
