#!/bin/bash

trace="sudo /home/raghav/log-compression-project/tracer/bin/trace"

run_autrace() {
    sudo auditctl -D
    cmd=$1
    out=$2
    pid=$($trace $cmd -r | grep -oE "[0-9]+")
    echo "pid" $pid
    sudo ausearch -r -p $pid  > $out
}

sudo auditctl -D
# Demonstrates the affect of loops on provenance graph.
cd ../c_tests
run_autrace "./testCase5 test.txt" "../examples/testCase.audit"
