#!/bin/bash

input_file="data.jsonl"
output_file="data2.jsonl"
subset_string="https://testmaps-v2.metria.se/geokodning/Geocode?"

# Using awk to delete subset string from each line
awk -v subset="$subset_string" '{gsub(subset, ""); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"  


input_file="data2.jsonl"
output_file="data3.jsonl"
subset_string="Give me the relevant geodata to the following url"
replacement_string="Give me the location data that has most in common with the following address"

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"

input_file="data3.jsonl"
output_file="data4.jsonl"
subset_string="?address="
replacement_string=""

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"  

input_file="data4.jsonl"
output_file="data5.jsonl"
subset_string="&maxAnswers=1&replyExtent=L"
replacement_string=""

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"  

input_file="data5.jsonl"
output_file="data6.jsonl"
subset_string="|4110"
replacement_string=""

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"  

input_file="data6.jsonl"
output_file="data7.jsonl"
subset_string="|3136"
replacement_string=""

# Using awk to replace subset string with replacement string in each line
awk -v subset="$subset_string" -v replacement="$replacement_string" '{gsub(subset, replacement); print}' "$input_file" > "$output_file"


echo "Conversion complete. Output written to $output_jsonl_file"  

  