#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 300 -i 25 -c config.yaml -w ./violations"

FILE="100%_fast_improved mutate.txt"

for ((i=1; i<=15; i++)); do
    echo "************************"
    echo "running iter $i..."
    echo "************************" >> "$FILE"
    echo "iter $i:" >> "$FILE"
    $COMMAND >> "$FILE" 2>&1
    echo "************************" >> "$FILE"
    echo "iter $i complete"
    echo "************************" >> "$FILE"
done

echo "************************"
echo "************************"
echo "************************"
echo "DONE"
echo "************************"
echo "************************"
echo "************************"