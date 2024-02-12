import json
from faker import Faker
import datetime
import os
import requests
import random

fake = Faker() 
output_data = []

num_messages = 200  # Adjust the number of messages

# Create output directory
output_dir = "slack_export"
os.makedirs(output_dir, exist_ok=True)

# Function to download images (New Addition)
def download_image(url, destination_folder):
    filename = url.split("/")[-1]

    response = requests.get(url, stream=True) 
    response.raise_for_status() 

    content_type = response.headers.get('Content-Type')  # E.g., 'image/jpeg'
    extension =  '.jpg' if content_type == 'image/jpeg' else '.png' # Deduce common extensions
    filename = url.split("/")[-1] + extension  # Adjust if filename needs more context 
    file_path = os.path.join(destination_folder, filename)

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(1024): 
            f.write(chunk)   
    return filename 

# Process messages 
output_data = []
fake = Faker()

for _ in range(num_messages):
    username = fake.name()
    timestamp = fake.date_time_between(start_date='-1y', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
    text = fake.sentence(nb_words=random.randint(5, 20))  # Varying sentence lengths

    image_path = None
    # Image Handling  
    if random.random() < 0.3:  # Simulate images in some messages
        # Use faker to get an image URL
        image_url = fake.image_url() 
        try:
            image_filename = download_image(image_url, output_dir)
            image_path = os.path.join(output_dir, image_filename)  # Build relative image path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {image_url}: {e}") 

    # Build output structure for JSON
    output_line = {
        "user": username,
        "timestamp": timestamp,
        "text": text,
        "image_path": image_path  
    }
    output_data.append(output_line) 


with open("conversation.json", "w") as f:
    json.dump(output_data, f, indent=4)  # Pretty formatting 
