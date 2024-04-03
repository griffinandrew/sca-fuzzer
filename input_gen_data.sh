#!/bin/bash

COMMAND="rvzr fuzz -s base.json -n 1000 -i 25 -c config.yaml -w ./violations"

FILE="output_dumb_50_inputs.txt"

for ((i=1; i<=15; i++)); do
    echo "************************\n"
    echo "running iter $i..."
    echo "************************\n" >> "$FILE"
    echo "iter $i:\n" >> "$FILE"
    $COMMAND >> "$FILE" 2>&1
    echo "************************\n" >> "$FILE"
    echo "iter $i complete"
    echo "************************\n" >> "$FILE"
done

echo "************************\n"
echo "************************\n"
echo "************************\n"
echo "DONE"
echo "************************\n"
echo "************************\n"
echo "************************\n"