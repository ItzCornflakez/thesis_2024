#!/bin/bash

input_file="input.csv"
output_file="input_3.csv"

awk 'BEGIN { FS=OFS="," } { gsub(/"/, "", $0); print }' "$input_file" > "$output_file"

echo "Quotes removed from $input_file and saved to $output_file"