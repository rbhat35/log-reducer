#!/bin/bash
sudo service neo4j stop
sudo rm -rf /var/lib/neo4j/data/databases/graph.db
sudo service neo4j start

cd examples
./run_tests_c.sh

cd ../parser
python parser.py ../examples/testCase1.audit

sleep 10

sudo ./neo4j-load-csv.sh .
