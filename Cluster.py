import argparse
import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np

def cluster_coordinates(input_csv, epsilon, min_samples):
    # Load the CSV file
    data = pd.read_csv(input_csv)
    print("Reading CSV is successful.")

    # Extract latitude and longitude
    coords = data[['latitude', 'longitude']].values

    # Apply DBSCAN clustering
    db = DBSCAN(eps=epsilon, min_samples=min_samples, metric='haversine').fit(np.radians(coords))
    labels = db.labels_

    # Add the cluster labels to the data
    data['cluster'] = labels

    # Store clustered coordinates with increasing filenames
    clustered_coords = {}
    for cluster_label in np.unique(labels):
        if cluster_label != -1:  # Ignore noise points
            cluster_data = data[data['cluster'] == cluster_label]
            clustered_coords[f'AOI{cluster_label + 1}'] = cluster_data[['latitude', 'longitude']].values

    print("First 20 clustered coordinates:")
    for i, (aoi, coords) in enumerate(clustered_coords.items()):
        if i >= 20:
            break
        print(f"{aoi}: {coords}")

    return clustered_coords

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cluster coordinates from CSV.')
    parser.add_argument('--input_csv', type=str, default='/Users/joshmanto/Downloads/BB/tree-semantics/lats-longs-csv/locations.csv', help='Input CSV file with coordinates')
    parser.add_argument('--epsilon', type=float, default=0.01, help='Maximum distance between two points for them to be considered in the same neighborhood')
    parser.add_argument('--min_samples', type=int, default=5, help='Minimum number of points required to form a dense region (cluster)')

    args = parser.parse_args()
    clustered_coords = cluster_coordinates(args.input_csv, args.epsilon, args.min_samples)
