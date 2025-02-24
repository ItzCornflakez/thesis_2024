from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import csv
import os
from PIL import Image

# Set up the web driver (e.g., Chrome)
driver = webdriver.Chrome()

tried = False
new_site = 0

# Create 'imgs' folder if it doesn't exist
if not os.path.exists('imgs'):
    os.makedirs('imgs')

# Create 'imgs_names' folder if it doesn't exist
if not os.path.exists('imgs_names'):
    os.makedirs('imgs_names')

# Function to take a screenshot of a specific coordinate
def capture_map_image(lat, lon, zoom_level, file_name, crop_margin=100):

    global tried
    global new_site

    new_site+=1

    # Construct URL with latitude, longitude, and zoom level
    map_url = f"https://kartbild.com/#{zoom_level}/{lat}/{lon}"
    
    # Load the map
    driver.get(map_url)
    
    # Give it some time to load
    if(new_site%5 == 1):
        time.sleep(3)
        print(1)
    
    # Attempt to click on the radio button element after loading
    if not tried:
        try:
            # Locate the <span> element with text "sattelit"
            span_element = driver.find_element(By.XPATH, '//span[contains(text(), "satellit")]')
            
            # Locate the parent <div> of this span
            parent_div = span_element.find_element(By.XPATH, './ancestor::div')
            
            # Find the radio input within the same parent <div>
            radio_button = parent_div.find_element(By.XPATH, './/input[@type="radio" and contains(@class, "leaflet-control-layers-selector")]')
            radio_button.click()
            tried = True
            time.sleep(1)
        except NoSuchElementException:
            print("Radio button not found on the page.")
        

    time.sleep(1)
    
    # Capture a screenshot and save it temporarily
    temp_file_path = os.path.join('imgs', 'temp_screenshot.png')
    driver.save_screenshot(temp_file_path)
    
    # Open the screenshot and crop it
    with Image.open(temp_file_path) as img:
        width, height = img.size
        cropped_img = img.crop((crop_margin, crop_margin, width - (3 * crop_margin), height - crop_margin))
        
        # Save the cropped image to the desired file path
        file_path = os.path.join('imgs', file_name)
        cropped_img.save(file_path)
    
    # Remove the temporary screenshot file
    os.remove(temp_file_path)

def add_map_caption(city, file_number):
    # Construct the file path
    filename = os.path.join("imgs_names", f"caption_{file_number}.txt")
    # Open the file in write mode and write the text
    with open(filename, "w") as file:
        file.write(city)

city_coordinates = []

# Replace 'your_file.csv' with the path to your CSV file
with open('se.csv', mode='r') as file:
    # Read the CSV file
    csv_reader = csv.DictReader(file)

    # Iterate over each row
    for row in csv_reader:
        # Replace 'Column1' and 'Column2' with the column names you want to read
        lat_data = float(row['lat'])
        long_data = float(row['lng'])
        city_data = row['city']

        small_inc = 0.01
        # Add the pair as a tuple to the list
        # Getting 10 different images of each city for a total dataset of above 1000 city images
        city_coordinates.append((city_data, lat_data, long_data))
        city_coordinates.append((city_data, lat_data+small_inc, long_data))
        city_coordinates.append((city_data, lat_data-small_inc, long_data))
        city_coordinates.append((city_data, lat_data, long_data+small_inc))
        city_coordinates.append((city_data, lat_data, long_data-small_inc))
        city_coordinates.append((city_data, lat_data+small_inc, long_data+small_inc))
        city_coordinates.append((city_data, lat_data+small_inc, long_data-small_inc))
        city_coordinates.append((city_data, lat_data-small_inc, long_data+small_inc))
        city_coordinates.append((city_data, lat_data-small_inc, long_data-small_inc))
        city_coordinates.append((city_data, lat_data+(small_inc*2), long_data))

# Loop through coordinates and capture screenshots
for idx, (city, lat, lon) in enumerate(city_coordinates):
    file_name = f"city_{idx}.png"
    capture_map_image(lat, lon, zoom_level=14, file_name=file_name)
    add_map_caption(city, idx)

# Close the driver
driver.quit()