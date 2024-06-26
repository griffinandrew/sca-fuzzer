#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 300 -i 25 -c config.yaml -w ./violations"

FILE="25%_taint_smart.txt"

for ((i=1; i<=20; i++)); do
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