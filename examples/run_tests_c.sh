#!/bin/bash

trace="sudo /home/sanya/log-compression-project/tracer/bin/trace"

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
run_autrace "../c_tests/testCase1.out" "testCase1.audit"
