#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 500 -i 25 -c config.yaml -w ./violations"

FILE="output_dumb_50_inputs.txt"

for ((i=1; i<=15; i++)); do
    echo "************************"
    echo "running iter $i..."
    echo "************************" >> "$FILE"
    echo "iter $i:\n" >> "$FILE"
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