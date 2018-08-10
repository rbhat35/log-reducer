#!/bin/bash

run_autrace() {
    cmd=$1
    out=$2
    log_cmd=$(autrace $cmd -r | grep -oE "ausearch[^\']*")
    echo "$log_cmd"
    eval $log_cmd > $out
}

# Demonstrates the affect of loops on provenance graph.
run_autrace "./readloop 256.txt" "readloop_256.audit" &
run_autrace "./readloop 1024.txt" "readloop_1024.audit" 
