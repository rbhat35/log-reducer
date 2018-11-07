#!/bin/bash

trace="sudo /home/joey/log-compression/tracer/bin/trace"

run_autrace() {
    sudo auditctl -D
    cmd=$1
    out=$2
    pid=$($trace $cmd -r | grep -oE "[0-9]+")
    echo "pid" $pid
    sudo ausearch -r  -p $pid  > $out
}

sudo auditctl -D
# Demonstrates the affect of loops on provenance graph.
run_autrace "./readloop 256.txt" "readloop_256.audit"
run_autrace "./readloop 1024.txt" "readloop_1024.audit" 
