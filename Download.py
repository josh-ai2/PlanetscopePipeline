import os
import requests
from requests.auth import HTTPBasicAuth

# Constants
API_KEY = 'PLAKe8a128a493104644888a58e5a0b4b780'
ACTIVATION_LOG_FILE = '/Users/joshmanto/Downloads/BB/tree-semantics/activation_log.txt'
DOWNLOAD_LOG_FILE = '/Users/joshmanto/Downloads/BB/tree-semantics/download_log.txt'
ASSET_TYPE = 'ortho_analytic_4b'
ITEM_TYPE = 'PSScene'


def remove_duplicates_from_log(log_file):
    unique_entries = set()
    cleaned_entries = []

    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line not in unique_entries:
                    unique_entries.add(line)
                    cleaned_entries.append(line)

    # Write back the cleaned entries to the log file
    with open(log_file, 'w') as file:
        file.writelines(cleaned_entries)


def extract_active_image_ids(log_file):
    image_ids = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                image_id, status = line.strip().split(': ')
                if status == 'active':
                    image_ids.append(image_id)
    return image_ids


def get_download_link(image_id, api_key):
    # Construct the URL for the asset
    url = f'https://api.planet.com/data/v1/item-types/{ITEM_TYPE}/items/{image_id}/assets'
    # Make the request to the Planet API
    result = requests.get(url, auth=HTTPBasicAuth(api_key, ''))
    if result.status_code == 200:
        download_link = result.json()[ASSET_TYPE]['location']
        return download_link
    else:
        print(f"Failed to get download link for {image_id}. Status code: {result.status_code}")
        return None


def log_download_link(image_id, download_link, log_file):
    with open(log_file, 'a') as log:
        log.write(f"{image_id}: {download_link}\n")


def main():
    # Remove duplicates from the activation log
    remove_duplicates_from_log(ACTIVATION_LOG_FILE)
    print("Duplicates removed from activation log.")

    # Extract active image IDs
    image_ids = extract_active_image_ids(ACTIVATION_LOG_FILE)
    print(f"Found {len(image_ids)} active image IDs.")

    # Prompt user and generate download links
    for image_id in image_ids:
        user_input = input(f"Do you want to generate a download link for {image_id}? (Y/N): ").strip().upper()
        if user_input == 'Y':
            download_link = get_download_link(image_id, API_KEY)
            if download_link:
                log_download_link(image_id, download_link, DOWNLOAD_LOG_FILE)
                print(f"Download link for {image_id}: {download_link} has been logged.")


if __name__ == "__main__":
    main()
