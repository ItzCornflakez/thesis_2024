#!/bin/bash

input_file="output.csv"
output_file="output_3.csv"

# Use awk to replace double quotes with escaped double quotes and write to the output file
awk -F, 'BEGIN {OFS=FS} {for (i=1; i<=NF; i++) gsub(/"/, "\\\"",$i)} 1' "$input_file" > "$output_file"

echo "Quotes replaced and output written to $output_file"