#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 100 -i 10  -c config.yaml -w ./violations"

FILE="output_all_mutate.txt"

for ((i=1; i<=15; i++)); do
    echo "************************"
    echo "running iter $i..."
    echo "************************" >> "$FILE"
    echo "iter $i:" >> "$FILE"
    $COMMAND >> "$FILE" 2>&1
    echo "iter $i complete"
done

echo "complete"