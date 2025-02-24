#!/bin/bash

input_file="input_3.csv"
output_file="output_3.csv"
output_jsonl_file="data.jsonl"
instruction="Give me the relevant geodata to the following url"

# Check if input and output files exist
if [ ! -f "$input_file" ] || [ ! -f "$output_file" ]; then
  echo "Input or output file not found."
  exit 1
fi

# Read input and output files line by line and create JSONL format, skipping the first line in the input file
{ IFS= read -r _; while IFS= read -r input_line && IFS= read -r output_line <&3; do
  jsonl_line="{\"text\": \"### Human: $instruction: $input_line ### Assistant: $output_line\"}"
  echo "$jsonl_line" >> "$output_jsonl_file"
done; } < "$input_file" 3< "$output_file"

echo "Conversion complete. Output written to $output_jsonl_file"