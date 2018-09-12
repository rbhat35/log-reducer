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
