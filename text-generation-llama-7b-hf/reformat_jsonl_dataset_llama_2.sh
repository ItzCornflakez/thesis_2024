#!/bin/bash

input_file="data7.jsonl"
output_file="data8.jsonl"
subset_string="|"

# Using awk to delete subset string from each line
sed "s/$subset_string//g" "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"


input_file="data8.jsonl"
output_file="data9.jsonl"
subset_string="Give me the location data that has most in common with the following address"
replacement_string="Give me the location data in the form of a xml object that has most in common with the following address"

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"