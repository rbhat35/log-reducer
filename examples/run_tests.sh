#!/bin/bash

run_autrace() {
    cmd=$1
    out=$2
    pid=$(autrace $cmd -r | grep -oE "[0-9]+")
    ausearch -r -p $pid  > $out
}

auditctl -D
# Demonstrates the affect of loops on provenance graph.
run_autrace "./readloop 256.txt" "readloop_256.audit"
run_autrace "./readloop 1024.txt" "readloop_1024.audit" 
