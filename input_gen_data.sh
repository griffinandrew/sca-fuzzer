#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 1000 -i 50 -c config.yaml -w ./violations"

FILE="output_33_mutate_100_inputs.txt"

for ((i=1; i<=15; i++)); do
    echo "************************"
    echo "running iter $i..."
    echo "************************" >> "$FILE"
    echo "iter $i:" >> "$FILE"
    $COMMAND >> "$FILE" 2>&1
    echo "iter $i complete"
done

echo "complete"