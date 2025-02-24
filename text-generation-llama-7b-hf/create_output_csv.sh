#!/bin/bash

input_file="input.csv"
output_file="output.csv"
api_base_url="" # Fill in base url for api targeted here

# Ensure the output file is empty or create it if it doesn't exist
echo -n > "$output_file"

# Read the first line to skip headers
read -r header_line < "$input_file"

# Loop through each subsequent line in the input CSV file
while IFS=, read -r api_request
do

    api_request=$(echo "$api_request" | tr -d '"')

    # Print information about the command being executed
    #echo "Executing curl command:"
    #echo "URL: $api_request"

    # Execute the curl command with basic authentication
    response=$(curl -s $api_request -u test_user:123)

    # Print the result
    #echo "Response:"
    #echo $response

    response=$(echo "$response" | tr -d '\n')

    # Append the result to the output CSV file
    echo "$response" >> "$output_file"

    # Separator for better readability
    #echo "----------------------------------"

done < <(tail -n +2 "$input_file")

echo "Processing complete. Results are in $output_file"