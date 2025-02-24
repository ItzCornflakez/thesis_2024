import json
import re

# Function to process a single row
def process_row(row):
    try:
        # Parse the JSON
        data = json.loads(row)
        
        # Extract the "text" field
        text_field = data.get('text', '')
        if "### Assistant:" not in text_field:
            return {"text": "Invalid structure"}
        
        # Split into Human and Assistant parts
        human_part, assistant_part = text_field.split("### Assistant: ")

        # Extract the search address from the Human text
        # This regex now captures any address pattern, regardless of context or formatting
        search_address_match = re.search(r"address: (.*?)$", human_part, re.MULTILINE)
        if search_address_match:
            search_address = search_address_match.group(1).strip()
        else:
            search_address = "Address not found"

        if search_address == "Okänd adress , Okänd":
            return None  # Discard row

        # Extract the first address from the Assistant XML
        match = re.search(r'address="(.*?)"', assistant_part)
        if match:
            first_address = match.group(1)
            # Replace HTML entities
            first_address = (first_address
                             .replace("&#233;", "é")
                             .replace("&#246;", "ö")
                             .replace("&#228;", "ä")
                             .replace("&#229;", "å"))
        else:
            first_address = "Address not found"

        # Skip rows where the Assistant part is "Address not found"
        if first_address == "Address not found":
            return None  # Discard row

        # Modify the Human text and construct the new row
        modified_human_text = f"### Human: Give me the location data that has the most in common with the following address: {search_address} ###"
        processed_text = f"{modified_human_text} Assistant: {first_address}"
        
        # Return the updated row
        return {"text": processed_text}
    except Exception as e:
        return {"text": f"Error processing row: {str(e)}"}

# Process a JSONL file
def process_jsonl_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Process each row
            processed_row = process_row(line.strip())
            if processed_row:  # Only write valid rows
                outfile.write(json.dumps(processed_row, ensure_ascii=False) + '\n')


# Input and output file paths
input_file = 'data9.jsonl'
output_file = 'data10.jsonl'

# Process the file
process_jsonl_file(input_file, output_file)

print(f"Processing complete. Output saved to {output_file}.")
