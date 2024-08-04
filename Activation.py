import os
import requests
from requests.auth import HTTPBasicAuth

# Constants
API_KEY = 'PLAKe8a128a493104644888a58e5a0b4b780'
THUMB_ACTIVATION_DIR = '/Users/joshmanto/Downloads/BB/tree-semantics/thumb_activation'
ASSET_TYPE = 'ortho_analytic_4b'
ITEM_TYPE = 'PSScene'
LOG_FILE = 'activation_log.txt'
ANOMALY_LOG_FILE = 'anomaly_log.txt'

def extract_image_ids(directory):
    image_ids = []
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            # Extract the image ID (before the first underscore)
            image_id = filename.split('_cloud_')[0]
            image_ids.append(image_id)
    return image_ids

def authenticate(api_key):
    response = requests.get('https://api.planet.com/data/v1', auth=HTTPBasicAuth(api_key, ''))
    if response.status_code == 200:
        print("Successfully authenticated.")
    else:
        print(f"Authentication failed with status code: {response.status_code}")
    return response.status_code

def check_asset_status(image_id, api_key, asset_type):
    # Construct the URL for the asset
    url = f'https://api.planet.com/data/v1/item-types/{ITEM_TYPE}/items/{image_id}/assets'
    # Make the request to the Planet API
    result = requests.get(url, auth=HTTPBasicAuth(api_key, ''))
    if result.status_code == 200:
        asset_status = result.json()[asset_type]['status']
        return asset_status, result.json()
    else:
        return f"Failed to get asset status. Status code: {result.status_code}", None

def activate_asset(image_id, asset_info, api_key, asset_type):
    links = asset_info[asset_type]["_links"]
    activation_link = links["activate"]
    self_link = links["_self"]

    # Request activation of the asset
    activate_result = requests.get(activation_link, auth=HTTPBasicAuth(api_key, ''))
    if activate_result.status_code == 202:
        print(f"Activation requested for {image_id}.")
        # Check activation status
        activation_status_result = requests.get(self_link, auth=HTTPBasicAuth(api_key, ''))
        activation_status = activation_status_result.json()["status"]
        print(f"Activation status for {image_id}: {activation_status}")
    else:
        print(f"Failed to request activation for {image_id}. Status code: {activate_result.status_code}")

def log_activation_status(image_id, status, log_file):
    if not is_already_logged(image_id, log_file):
        with open(log_file, 'a') as log:
            log.write(f"{image_id}: {status}\n")

def is_already_logged(image_id, log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as log:
            lines = log.readlines()
            for line in lines:
                if line.startswith(image_id):
                    return True
    return False

def main():
    # Extract image IDs from filenames in thumb_activation directory
    image_ids = extract_image_ids(THUMB_ACTIVATION_DIR)
    print(f"Found {len(image_ids)} image IDs.")
    print("Image IDs:", image_ids)

    # Authenticate
    auth_status = authenticate(API_KEY)
    if auth_status != 200:
        return

    # Check the activation status of the specific asset
    print(f"We are now going to check for status (active or not) for asset type '{ASSET_TYPE}'.")
    for i, image_id in enumerate(image_ids):
        if i < 5:
            status, asset_info = check_asset_status(image_id, API_KEY, ASSET_TYPE)
            print(f"Asset status for {image_id} ({ASSET_TYPE}): {status}")

            if status == 'inactive':
                user_input = input(f"Do you want to activate {image_id}? (Y/N): ").strip().upper()
                if user_input == 'Y':
                    activate_asset(image_id, asset_info, API_KEY, ASSET_TYPE)
        else:
            remaining = len(image_ids) - i
            user_input = input(f"Do you want to activate the remaining {remaining} assets? (Y/N): ").strip().upper()
            if user_input == 'Y':
                for image_id in image_ids[i:]:
                    status, asset_info = check_asset_status(image_id, API_KEY, ASSET_TYPE)
                    if status == 'inactive':
                        activate_asset(image_id, asset_info, API_KEY, ASSET_TYPE)
            break

    # Check activation status and log results
    print("Checking activation status of all assets and logging results.")
    for image_id in image_ids:
        status, _ = check_asset_status(image_id, API_KEY, ASSET_TYPE)
        if status == 'active':
            log_activation_status(image_id, status, LOG_FILE)
        else:
            log_activation_status(image_id, status, ANOMALY_LOG_FILE)

if __name__ == "__main__":
    main()
