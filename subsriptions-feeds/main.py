import os
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import subprocess

# Set up the API key and endpoint
os.environ['PL_API_KEY'] = 'PLAKe8a128a493104644888a58e5a0b4b780'
PLANET_API_KEY = os.getenv('PL_API_KEY')
BASE_URL = "https://api.planet.com/analytics/"

# Set up a session and authenticate
session = requests.Session()
session.auth = (PLANET_API_KEY, "")

# Test the connection
res = session.get(BASE_URL)
print(res.status_code)  # Should print 200 if the connection is successful
print("if 200 shows then authentication is successful")
print(res.text)  # Print the response body


def read_coordinates(csv_file):
    df = pd.read_csv(csv_file, usecols=['EA_GPS_LO', 'EA_GPS_LA'])
    df.columns = ['longitude', 'latitude']  # Rename columns for consistency
    return df


def calculate_bounding_box(coordinates):
    min_lon, max_lon = coordinates['longitude'].min(), coordinates['longitude'].max()
    min_lat, max_lat = coordinates['latitude'].min(), coordinates['latitude'].max()
    bounding_box = Polygon([
        (min_lon, min_lat),
        (min_lon, max_lat),
        (max_lon, max_lat),
        (max_lon, min_lat),
        (min_lon, min_lat)
    ])
    return bounding_box


def get_feeds():
    response = session.get(f"{BASE_URL}/feeds")
    response.raise_for_status()
    return response.json()


def list_subscriptions(feed_id):
    response = session.get(f"{BASE_URL}/feeds/{feed_id}/subscriptions")
    response.raise_for_status()
    return response.json()


def create_geodataframe(coordinates):
    geometry = [Point(xy) for xy in zip(coordinates['longitude'], coordinates['latitude'])]
    gdf = gpd.GeoDataFrame(coordinates, geometry=geometry)
    return gdf


def visualize_geodataframe(gdf):
    gdf.plot()


def query_region_based_filtering():
    bbbox = "121.771088,31.209278,121.907043,31.309062"
    url = f"https://api.planet.com/analytics/collections/886b4dbb-b878-4f6b-b000-0d96cbf71d4d/items?bbbox={bbbox}"
    response = session.get(url)
    print("Region Based Filtering Response:", response.json())


def query_datetime_filtering():
    datetime = "2019-01-18T02:08:40.761735Z"
    url = f"https://api.planet.com/analytics/collections/886b4dbb-b878-4f6b-b000-0d96cbf71d4d/items?datetime={datetime}"
    response = session.get(url)
    print("Datetime Based Filtering Response:", response.json())


def main():
    csv_file = '/locations.csv'
    coordinates = read_coordinates(csv_file)

    # Calculate the bounding box
    bounding_box = calculate_bounding_box(coordinates)

    # Authenticate and get feeds
    feeds = get_feeds()
    print("Feeds:", feeds)

    # Remove the part that creates a feed

    # List subscriptions (assuming a valid feed_id)
    if feeds['data']:
        feed_id = feeds['data'][0]['id']
        subscriptions = list_subscriptions(feed_id)
        print("Subscriptions:", subscriptions)
    else:
        print("No feeds available.")

    # Query using region based filtering
    query_region_based_filtering()

    # Query using datetime based filtering
    query_datetime_filtering()

    # Create and visualize GeoDataFrame
    gdf = create_geodataframe(coordinates)
    visualize_geodataframe(gdf)


if __name__ == "__main__":
    main()
