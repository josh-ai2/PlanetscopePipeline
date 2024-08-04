import os
import requests
from requests.auth import HTTPBasicAuth

API_KEY = 'PLAKe8a128a493104644888a58e5a0b4b780'
OUTPUT_DIR = 'thumbnail_dump'
LOG_FILE = 'thumbnails.log'

def download_image(thumbnail_url, image_id, cloud_cover, date, output_dir):
    response = requests.get(thumbnail_url, auth=HTTPBasicAuth(API_KEY, ''))
    if response.status_code == 200:
        filename = f"{image_id}_cloud_{cloud_cover}_date_{date}.jpg"
        image_path = os.path.join(output_dir, filename)
        with open(image_path, 'wb') as image_file:
            image_file.write(response.content)
        print(f"Downloaded and saved {filename}")
    else:
        print(f"Failed to download {thumbnail_url}. Status code: {response.status_code}")

def main():
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the log file
    with open(LOG_FILE, 'r') as log_file:
        log_content = log_file.readlines()

    # Parse the log file and download images
    for i in range(len(log_content)):
        if log_content[i].startswith("http"):
            thumbnail_url = log_content[i].strip()
            info_line = log_content[i + 1].strip()
            parts = info_line.split(", ")
            image_id = parts[0].split(": ")[1]
            cloud_cover = parts[1].split(": ")[1]
            date = parts[2].split(": ")[1]
            download_image(thumbnail_url, image_id, cloud_cover, date, OUTPUT_DIR)

if __name__ == "__main__":
    main()
