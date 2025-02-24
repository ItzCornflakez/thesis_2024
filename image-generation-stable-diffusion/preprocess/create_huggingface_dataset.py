import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from PIL import Image
from io import BytesIO

# Directories for images and captions
image_dir = "imgs"  # Replace with your folder of images
caption_dir = "imgs_names"  # Replace with your folder of captions

# Output directory for the dataset
output_dir = "city-blip-captions"
data_dir = os.path.join(output_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# Function to encode image as binary data with resizing to 512x512
def encode_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")  # Ensure the image is in RGB format
        img = img.resize((512, 512), Image.ANTIALIAS)  # Resize to 512x512
        buffer = BytesIO()
        img.save(buffer, format="PNG")  # Save as PNG
        return buffer.getvalue()  # Return binary data

# Gather data
data = []
for caption_file in os.listdir(caption_dir):
    print("Processing caption file:", caption_file)
    if caption_file.endswith(".txt"):
        # Extract the number from the caption file name (e.g., "caption_1.txt" -> "1")
        caption_number = Path(caption_file).stem.split("_")[1]
        print("Caption number:", caption_number)

        # Read the city name from the caption file
        caption_path = os.path.join(caption_dir, caption_file)
        with open(caption_path, "r") as f:
            city_name = f.read().strip()
        transformed_caption = f"A topdown satellite image of {city_name}"

        # Match the corresponding image file
        image_file = f"city_{caption_number}.png"
        image_path = os.path.join(image_dir, image_file)
        if os.path.exists(image_path):
            print("Found matching image:", image_path)
            encoded_image = encode_image(image_path)  # Encode image as binary data
            data.append({"image": encoded_image, "text": transformed_caption})
        else:
            print("No matching image for caption:", caption_file)

df = pd.DataFrame(data)
print("DataFrame preview:")
print(df.head())

if not df.empty:
    # Split into Parquet files
    n_files = 2  # Adjust this based on your dataset size
    split_dfs = np.array_split(df, n_files)

    for i, split_df in enumerate(split_dfs):
        file_name = f"train-{i:05d}-of-{n_files:05d}.parquet"
        file_path = os.path.join(data_dir, file_name)
        split_df.to_parquet(file_path, index=False)

# Compute dataset size
dataset_size = int(sum([split_df.memory_usage(deep=True).sum() for split_df in split_dfs]))

# Create JSON metadata
dataset_infos = {
    "itzcornflakez--map-image-captions": {
        "description": "A dataset of satellite images of cities with captions.",
        "citation": "",
        "homepage": "",
        "license": "",
        "features": {
            "image": {
                "decode": True,
                "id": None,
                "_type": "Image"
            },
            "text": {
                "dtype": "string",
                "id": None,
                "_type": "Value"
            }
        },
        "post_processed": None,
        "supervised_keys": None,
        "task_templates": None,
        "builder_name": None,
        "config_name": None,
        "version": None,
        "splits": {
            "train": {
                "name": "train",
                "num_bytes": dataset_size,  # Convert to int
                "num_examples": int(len(df)),  # Convert to int
                "dataset_name": "map-image-captions"
            }
        },
        "download_checksums": None,
        "download_size": dataset_size,  # Convert to int
        "post_processing_size": None,
        "dataset_size": dataset_size,  # Convert to int
        "size_in_bytes": 2 * dataset_size  # Adjust if required
    }
}

# Write JSON metadata to file
with open(os.path.join(output_dir, "dataset_infos.json"), "w") as f:
    json.dump(dataset_infos, f, indent=4)

print(f"Dataset created successfully at {output_dir}")
