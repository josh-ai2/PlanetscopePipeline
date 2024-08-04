# Tree Semantic Classifier

This project involves querying, clustering, and downloading satellite images from Planet.com using their API. It includes three main Python scripts: `query.py`, `thumbnail.py`, and `cluster.py`. Each script is responsible for different parts of the workflow.

## Overview

- **Cluster.py**: Clusters geographical coordinates from a CSV file using the DBSCAN algorithm.
  - Displays the Area of Interests in increasing order (e.g., AOI1, AOI2).
  - AOI1 and AOI2 are stored as NDARRAY objects.
  - Sample usage: `python Cluster.py --input_csv path/to/locations.csv --epsilon 0.01 --min_samples 5`
  
- **Query.py**: Queries the Planet API for satellite images based on clustered coordinates, filtering by date range and cloud cover, and logs thumbnail URLs and metadata into a thumbnail log file.
  - Submits POST requests to the Planet.com API endpoint to query images that match the latitudes and longitudes from our CSV file.
  - Converts NDArray objects from `Cluster.py` to lists, then to JSON, and finally makes POST requests to the Planet.com API endpoint.
  - Sample usage: `python Query.py --api_key your_api_key --start_date YYYY-MM-DD --end_date YYYY-MM-DD --cloud_cover 0.5 --aoi 2 --input_csv path/to/locations.csv --result_limit 5 --log_file thumbnails.log`

- **Thumbnail.py**: Downloads and saves the thumbnails of the queried satellite images, renaming them based on metadata.
  - Sample usage: `python Thumbnail.py --log_file thumbnails.log`
 
- **Example Log File Entry**
`Results for AOI2:
https://tiles.planet.com/data/v1/item-types/PSScene/items/20200121_092611_01_106b/thumb
Image ID: 20200121_092611_01_106b, Cloud Cover: 0.45, Date: 20200121`

## **PROJECT STILL UNDER PROGRESS**
Future implementations: 
1. Select and send image assets into API endpoint for activation
2. "CLIP" function to clip the downloaded images into our desired size (careful about the download quota)
3. Generate download links for each image 




