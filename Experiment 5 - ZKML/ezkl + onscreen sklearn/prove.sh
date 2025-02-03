#!/bin/bash

# Run ezkl prove in the background and capture its PID
# change accordingly to arguments you used
ezkl prove --compiled-circuit network.ezkl &
EZKL_PID=$!

echo "ezkl prove process started with PID: $EZKL_PID"

# Function to get memory usage
get_memory_usage() {
    ps -o rss= -p $1 | awk '{print $1/1024 " MB"}'
}

# Monitor memory usage every x seconds 
while kill -0 $EZKL_PID 2>/dev/null; do
    MEM_USAGE=$(get_memory_usage $EZKL_PID)
    echo "Current memory usage: $MEM_USAGE"
    sleep 1 # change as required
done

echo "ezkl prove process has finished."
