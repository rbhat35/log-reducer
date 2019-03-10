#!/bin/bash

trace="sudo /home/raghav/log-compression-project/tracer/bin/trace"

run_autrace() {
    sudo auditctl -D
    out=$1
    sudo ausearch -r  > $out
}

sudo auditctl -D
# Demonstrates the affect of loops on provenance graph.
run_autrace $1


