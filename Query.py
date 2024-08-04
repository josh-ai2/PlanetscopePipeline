import argparse
import requests
import json
import time
import importlib.util
from requests.auth import HTTPBasicAuth
from shapely.geometry import box, mapping


def create_bounding_box(coords):
    """Create a bounding box from coordinates."""
    lats, lons = zip(*coords)
    return box(min(lons), min(lats), max(lons), max(lats))


def create_filters(coords, start_date, end_date, cloud_cover):
    """Create filters for querying the Planet API."""
    bounding_box = create_bounding_box(coords)
    geojson_geometry = mapping(bounding_box)

    geometry_filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": geojson_geometry
    }

    date_range_filter = {
        "type": "DateRangeFilter",
        "field_name": "acquired",
        "config": {
            "gte": start_date,
            "lte": end_date
        }
    }

    cloud_cover_filter = {
        "type": "RangeFilter",
        "field_name": "cloud_cover",
        "config": {
            "lte": cloud_cover
        }
    }

    filters = {
        "type": "AndFilter",
        "config": [geometry_filter, date_range_filter, cloud_cover_filter]
    }

    print("Filters used for the query:")
    print(json.dumps(filters, indent=2))

    return filters


def load_clustered_coords(input_csv, epsilon, min_samples):
    # Import the Cluster.py module
    spec = importlib.util.spec_from_file_location("Cluster", "./Cluster.py")
    cluster_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cluster_module)

    # Run the cluster_coordinates function from Cluster.py
    return cluster_module.cluster_coordinates(input_csv, epsilon, min_samples)


def authenticate(api_key):
    response = requests.get('https://api.planet.com/data/v1', auth=HTTPBasicAuth(api_key, ''))
    if response.status_code == 200:
        print("Successfully authenticated.")
    else:
        print(f"Authentication failed with status code: {response.status_code}")
    return response.status_code


def search_for_images(filters, api_key, item_type="PSScene"):
    search_endpoint = "https://api.planet.com/data/v1/quick-search"
    search_request = {
        "item_types": [item_type],
        "filter": filters
    }

    search_result = requests.post(search_endpoint, auth=HTTPBasicAuth(api_key, ''), json=search_request)
    if search_result.status_code != 200:
        print(f"Error searching for images: {search_result.text}")
        return []

    geojson = search_result.json()

    return geojson.get('features', [])


def print_results(aoi_name, features, limit=5, log_file="thumbnails.log"):
    if not features:
        print(f"No results found for {aoi_name}.")
        return

    with open(log_file, 'a') as log:
        print(f"Number of images for {aoi_name}: {len(features)}")
        log.write(f"Results for {aoi_name}:\n")
        print("-" * 60)
        for feature in features[:limit]:
            thumbnail_url = feature['_links']['thumbnail']
            image_id = feature['id']
            acquired_date = feature['properties']['acquired'][:10].replace("-", "")
            cloud_cover = feature['properties']['cloud_cover']
            coordinates = feature['geometry']['coordinates']

            print(f"Image ID: {image_id}")
            print(f"Acquired: {feature['properties']['acquired']}")
            print(f"Cloud Cover: {cloud_cover}")
            print(f"Geometry: {feature['geometry']['type']} {coordinates}")
            print(f"Thumbnail: {thumbnail_url}")
            log.write(f"{thumbnail_url}\n")
            log.write(f"Image ID: {image_id}, Cloud Cover: {cloud_cover}, Date: {acquired_date}\n")
            print("-" * 60)
        print(f"Displayed first {limit} results for {aoi_name}.")
        print("\n" + "=" * 60 + "\n")
        time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description='Planet API Downloader - Part 2')
    parser.add_argument('--api_key', type=str, default='PLAKe8a128a493104644888a58e5a0b4b780',
                        help='API key for authentication')
    parser.add_argument('--start_date', type=str, default='2020-01-01T00:00:00.000Z', help='Start date for filtering')
    parser.add_argument('--end_date', type=str, default='2020-02-01T00:00:00.000Z', help='End date for filtering')
    parser.add_argument('--cloud_cover', type=float, default=0.5, help='Maximum cloud cover')
    parser.add_argument('--aoi', type=int, default=2, help='Number of AOIs to iterate over')
    parser.add_argument('--input_csv', type=str,
                        default='/Users/joshmanto/Downloads/BB/tree-semantics/lats-longs-csv/locations.csv',
                        help='Input CSV file with coordinates')
    parser.add_argument('--epsilon', type=float, default=0.01,
                        help='Maximum distance between two points for them to be considered in the same neighborhood')
    parser.add_argument('--min_samples', type=int, default=5,
                        help='Minimum number of points required to form a dense region (cluster)')
    parser.add_argument('--result_limit', type=int, default=5,
                        help='Limit for the number of image results to display per AOI')
    parser.add_argument('--log_file', type=str, default='thumbnails.log', help='Log file to store thumbnail URLs')

    args = parser.parse_args()

    api_key = args.api_key
    start_date = args.start_date
    end_date = args.end_date
    cloud_cover = args.cloud_cover
    aoi = args.aoi
    input_csv = args.input_csv
    epsilon = args.epsilon
    min_samples = args.min_samples
    result_limit = args.result_limit
    log_file = args.log_file

    # Authenticate the API key
    authenticate(api_key)

    # Clear the log file
    open(log_file, 'w').close()

    # Load clustered coordinates by running Cluster.py
    clustered_coords = load_clustered_coords(input_csv, epsilon, min_samples)

    for i, (aoi_name, aoi_coords) in enumerate(clustered_coords.items()):
        if i >= aoi:
            break
        print(f"Now printing results for {aoi_name}")
        # Convert numpy array to list
        aoi_coords_list = aoi_coords.tolist()
        # Create filters
        filters = create_filters(aoi_coords_list, start_date, end_date, cloud_cover)
        features = search_for_images(filters, api_key)
        print_results(aoi_name, features, limit=result_limit, log_file=log_file)


if __name__ == "__main__":
    main()
