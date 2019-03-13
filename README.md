Setup Instructions
===

Currently, this system is comprised of two parts:
1. A log parser, which takes the raw output of Linux Audit logs and forms two CSVs (`backwards.csv` and `forward.csv`) containing information to be stored.
2. A reduction algorithm, which takes these log files as input and produces a reduced version, the instructions of which can be found in the README reduction/. You will have to include a parser for your machine, if not using the one provided by us in parser/ (to generate the csvs that need to be reduced). Example csvs are provided in parser/. 

We have included instructions, as well as parsers in this repository, to use our code with the Linux Audit System (Version ######).


Linux Audit Instructions
===

If you would like to setup the system to trace your own files:
The tracing system is built on top of libaudit

```shell
sudo apt-get install python-audit auditd
cd tracer
mkdir bin
make trace
```

We have included a python script to parse the libaudit output:
```shell
cd parser
pip install -r requirements.txt
```

Example Graphs
===

There are two example graphs that can be used to verify the setup is correct
in the generate_audit_logs/ directory. Run the commands below to create the raw audit
logs. If `run_sample_tests.sh` is ran succesfully, two files will be created:
`readloop_1024.audit` and `readloop_256.audit`.

```shell
cd generate_audit_logs
make
./run_sample_tests.sh
```

* Note we have provided unit tests in `/c_tests/`. Run `./run_tests_c.sh` to generate audit logs for each test case.

The next task is parsing the logs, which will convert the audit format
into csv files that can be inserted into Neo4j. Neo4j is a graph database.
To create the csv files run the commands below, which will create two csv
files `forward.csv` and `backwards.csv`.

```shell
cd parser
python parser.py ../generate_audit_logs/readloop_256.audit
```

Note: This will generate two files: `forward.csv` and `backwards.csv` which store the parsed data.

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

Note: on some larger logs, you may see many errors on certain types of systems. This is a result of starting the audit system after files have been opened by the processes that are accessing them.


Optional Step: For small graphs and debugging, it may be helpful to visualize the unreduced and reduced graph.

To insert the data into Neo4j, run the following command:

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

You can view the graph visually by going to http://143.215.130.71:7474/browser/
in a browser. A tutorial on how to visualize the graph can be found here (https://neo4j.com/developer/guide-neo4j-browser/).

Note: You can also use `/parser/generate_graphs.sh` to generate audit logs, parse the logs, and graph them all in one step.

Contact: rsbhat2 "at" gmail "dot" com regarding any questions.
