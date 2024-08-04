# Tree Semantic Classifier

This project involves querying, clustering, and downloading satellite images from Planet.com using their API. It includes three main Python scripts: `query.py`, `thumbnail.py`, and `cluster.py`. Each script is responsible for different parts of the workflow.

## Overview

- **Cluster.py**: Clusters geographical coordinates from a CSV file using the DBSCAN algorithm.
- Displays the Area of Interests in increasing order (e.g. AOI1, AOI2).
- AOI1 and AOI2 are stored as NDARRAY objects.
- 
- **Query.py**:
- - Queries the Planet API for satellite images based on clustered coordinates, filtering by date range and cloud cover, and logs thumbnail URLs and metadata into a thumbnail log file.
- - Submit POST request into Planet.com API endpoint to query images that match the lats and longs we have in our CSV file.
- - NDArray object from Cluster.py are converted --> list --> JSON package --> POST request into Planet.com API endpoint 
    
- **Thumbnail.py**: Downloads and saves the thumbnails of the queried satellite images, renaming them based on metadata. 

## Cluster.py

This script reads geographical coordinates from a CSV file, clusters them using the DBSCAN algorithm, and outputs clustered coordinates.

**Usage**:
python Cluster.py --input_csv path/to/locations.csv --epsilon 0.01 --min_samples 5

## Query.py

**Usage**: 
python Query.py --api_key your_api_key --start_date YYYY-MM-DD --end_date YYYY-MM-DD --cloud_cover 0.5 --aoi 2 --input_csv path/to/locations.csv --result_limit 5 --log_file thumbnails.log

**Example Log File Entry**:
Results for AOI2:
https://tiles.planet.com/data/v1/item-types/PSScene/items/20200121_092611_01_106b/thumb
Image ID: 20200121_092611_01_106b, Cloud Cover: 0.45, Date: 20200121

## Thumbnail.py

**Usage**: 
python Thumbnail.py --log_file thumbnails.log

**PROJECT STILL UNDER PROGRESS**
Future implementations: 
1. 




