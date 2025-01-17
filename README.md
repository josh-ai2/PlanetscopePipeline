# Planetscope Pipeline

This project involves querying, clustering, and downloading satellite images from Planet.com using their API. It includes three main Python scripts: `query.py`, `thumbnail.py`, and `cluster.py`. Each script is responsible for different parts of the workflow.

![Diagram](.idea/diagram2.png)

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


- **Activation.py**: Activates image assets based on user input.
  - Reads image IDs from the `thumb_activation` folder and checks their activation status.
  - Prompts the user to activate image assets and logs the activation status in `activation_log.txt`.
  - Sample usage: `python Activation.py`
 


- **Download.py**: Generates download links for activated image assets based on user input.
  - Reads active image IDs from `activation_log.txt`.
  - Prompts the user to generate download links for each image asset and logs the download links in `download_log.txt`.
  - Sample usage: `python Download.py`
  

## Important Notes

1. Ensure that you move files from the `thumbnail_dump` folder into the `thumb_activation` folder before running `Activation.py`.
2. The `activation_log.txt` file logs the activation status of image IDs.
3. The `download_log.txt` file logs the download links for the image IDs.

## MAIN RESULTS: 

![RESULTS](.idea/diagram3.png)

   

## **PROJECT STILL UNDER PROGRESS**
Future implementations: 
1. ~~Select and send image assets into API endpoint for activation~~
2. "CLIP" function to clip the downloaded images into our desired size (careful about the download quota). 
3. ~~Generate download links for each image~~

## **CLIP FUNCTION IMPLEMENTATION** 
- The final implementation that we need to do is search customization -- being able to add more custom parameters. We improve Query.py, specifically when we package the JSON payload before we send the post request into their quick-search API endpoint. Our goal is to be able to simply have a 256x256 or 128x128 bounding box surrounding the lats and longs when we cluster them together.

## COREGISTER (TO BE IMPLEMENTED)**

- The coregistration tool ensures that images in a specified time series are spatially aligned, so that any feature in one image overlaps as precisely as possible with its position in any other image in the series.

This tool is designed to support coregistration of small areas of interest – contained within a single scene – and works best with high geographic overlap between scenes in the times series.

SOURCE: https://developers.planet.com/apis/orders/tools/

