import csv
import logging
import math
import os
import time
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import ee
import requests
from retry import retry
from tqdm import tqdm
import pandas as pd

# Initialize Earth Engine
service_account = "josh-service@ee-my-josh-ai.iam.gserviceaccount.com"
json_key = "/Users/joshmanto/Downloads/BB/tree-semantics/ee-my-josh-ai-d07c4aef378c.json"
ee.Initialize(
    ee.ServiceAccountCredentials(service_account, json_key), opt_url='https://earthengine-highvolume.googleapis.com')

# Define dataset dictionary globally to avoid pickling it
dico = {
    'landsat': {
        'dataset': ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA"),
        'resolution': 30,
        'RGB': ['B4', 'B3', 'B2'],
        'NIR': 'B5',
        'panchromatic': 'B8',
        'min': 0.0,
        'max': 0.4
    },
    'naip': {
        'dataset': ee.ImageCollection("USDA/NAIP/DOQQ"),
        'resolution': 0.6,
        'RGB': ['R', 'G', 'B'],
        'NIR': 'N',
        'panchromatic': None,
        'min': 0.0,
        'max': 255.0
    },
    'sentinel': {
        'dataset': ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED"),
        'resolution': 10,
        'RGB': ['B4', 'B3', 'B2'],
        'NIR': 'B8',
        'panchromatic': None,
        'min': 0.0,
        'max': 4500.0
    }
}

def boundingBox(lat, lon, size, res):
    earth_radius = 6371000
    angular_distance = math.degrees(0.5 * ((size * res) / earth_radius))
    osLat = angular_distance
    osLon = angular_distance
    xMin = lon - osLon
    xMax = lon + osLon
    yMin = lat - osLat
    yMax = lat + osLat
    return xMin, xMax, yMin, yMax

@retry(tries=10, delay=2, backoff=2)
def generateURL(coord, height, width, dataset, crs, output_dir, start_date, end_date, sharpened=False):
    lon, lat = coord
    description = f"{dataset}_image_{lat}_{lon}"
    # description = f"{dataset}_image_{lat}_{lon}_{start_date}_{end_date}"
    res = dico[dataset]['resolution']
    xMin, xMax, yMin, yMax = boundingBox(lat, lon, height, res)
    geometry = ee.Geometry.Rectangle([[xMin, yMin], [xMax, yMax]])
    filtered = dico[dataset]['dataset'].filterDate(start_date, end_date).filterBounds(geometry)
    if dataset == 'sentinel':
        cloud_pct = 10
        filtered = filtered.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_pct))
    image = filtered.median().clip(geometry)
    RGB = dico[dataset]['RGB']
    _min = dico[dataset]['min']
    _max = dico[dataset]['max']
    band_names = image.bandNames()
    bands_list = band_names.getInfo()
    if all(band in bands_list for band in RGB):
        image_vis = image.visualize(bands=RGB, min=_min, max=_max)
        try:
            url = image_vis.getDownloadUrl({
                'description': description,
                'region': geometry,
                'fileNamePrefix': description,
                'crs': crs,
                'fileFormat': 'GEO_TIFF',
                'region': geometry,
                'format': 'GEO_TIFF',
                'dimensions': [height, width]
            })
            response = requests.get(url)
            if response.status_code != 200:
                raise response.raise_for_status()
            with open(os.path.join(output_dir, f'{description}.tif'), 'wb') as fd:
                fd.write(response.content)
            logging.info(f'Done: {description}')
        except Exception as e:
            logging.exception(e)
        panchromatic_band = dico[dataset]['panchromatic']
        if sharpened and panchromatic_band in bands_list:
            try:
                hsv = image.select(RGB).rgbToHsv()
                sharpened = ee.Image.cat(
                    [hsv.select('hue'),
                     hsv.select('saturation'),
                     image.select(panchromatic_band)]).hsvToRgb()
            except Exception as e:
                logging.exception(e)
                pass
            try:
                sharpe_url = sharpened.getDownloadUrl({
                    'description': "sharpened"+description,
                    'region': geometry,
                    'fileNamePrefix': "sharpened"+description,
                    'crs': crs,
                    'fileFormat': 'GEO_TIFF',
                    'region': geometry,
                    'format': 'GEO_TIFF',
                    'dimensions': [height, width]
                })
                sharpe_response = requests.get(sharpe_url)
                if sharpe_response.status_code != 200:
                    raise sharpe_response.raise_for_status()
                with open(os.path.join(output_dir, f'sharpened_{description}.tif'), 'wb') as fd:
                    fd.write(sharpe_response.content)
                logging.info(f'Done: sharpened_{description}')
            except Exception as e:
                logging.exception(e)
                pass
    else:
        logging.info(f'Image at {(lat, lon)} has bands: {bands_list}')
        pass

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--filepath", help="path to coordinates csv file", default='/home/sr365/data-plus-22/durham_cordinate.csv',  type=str)
    parser.add_argument("-d", "--dataset", help="name of dataset to pull images from (sentinel, landsat, or naip)", default="sentinel", type=str)
    parser.add_argument("-s", "--start_date", help="start date for getting images", default='2022-03-21', type=str)
    parser.add_argument("-e", "--end_date", help="end date for getting images", default='2022-06-20', type=str)
    parser.add_argument("-he", "--height", help="height of output images (in px)", default=512, type=int)
    parser.add_argument("-w", "--width", help="width of output images (in px)", default=512, type=int)
    parser.add_argument("-o", "--output_dir", help="path to output directory", default="output_images/", type=str)
    parser.add_argument("-sh", "--sharpened", help="download pan-sharpened image (only available for Landsat)", default=False, type=bool)
    parser.add_argument('--parallel', action='store_true')
    parser.add_argument('--no-parallel', dest='parallel', action='store_false')
    parser.set_defaults(parallel=True)
    parser.add_argument("-pn", "--parallel_number", help="number of parallel processes", default=10, type=int)
    parser.add_argument('--redownload', action='store_true')
    parser.add_argument('--no-redownload', dest='redownload', action='store_false')
    parser.set_defaults(redownload=False)
    args = parser.parse_args()

    print(args)

    logging.basicConfig(
        filename=f'{args.dataset}_logger.log',
        filemode="w",
        level="INFO",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        logging.info(f"Directory {args.output_dir} created")
    else:
        print("Please delete output directory before retrying")

    lat_lon_only = partial(generateURL,
                           height=args.height,
                           width=args.width,
                           dataset=args.dataset,
                           crs='EPSG:3857',
                           output_dir=args.output_dir,
                           start_date=args.start_date,
                           end_date=args.end_date,
                           sharpened=args.sharpened)

    with open(args.filepath, 'r') as coords_file:
        next(coords_file)
        coords = csv.reader(coords_file, quoting=csv.QUOTE_NONNUMERIC)
        data = list(coords)

    if not args.redownload:
        print('The original length of coordinate is:', len(data))
        filelist = os.listdir(args.output_dir)
        for file in filelist:
            split_file_name = file.replace('.tif', '').split('_')
            lat = float(split_file_name[2])
            lon = float(split_file_name[3])
            lon_lat_list = [lon, lat]
            data.remove(lon_lat_list)
        print('After removing the ones already downloaded, now there are {} coordinates left'.format(len(data)))

    if args.parallel:
        pn = args.parallel_number
        export_start_time = time.time()
        with ProcessPoolExecutor(max_workers=pn) as executor:
            futures = [executor.submit(lat_lon_only, data[i]) for i in range(len(data))]
            for future in tqdm(futures):
                future.result()  # This will raise an exception if the worker function raised one
        export_finish_time = time.time()
    else:
        export_start_time = time.time()
        for i in tqdm(range(len(data))):
            lat_lon_only(data[i])
            time.sleep(1)
        export_finish_time = time.time()

    duration = export_finish_time - export_start_time
    num_requested = len(pd.read_csv(args.filepath))
    num_downloaded = len([name for name in os.listdir(args.output_dir) if os.path.isfile(os.path.join(args.output_dir, name))])
    result = f'Export complete! It took {duration:.2f} s ({duration/60:.2f} min) to download {num_downloaded} images out of {2*num_requested if args.sharpened else num_requested} requested from {args.filepath} using the {args.dataset} dataset'
    logging.info(result)
    print(result)
    with open('results.txt', 'a') as f:
        f.write(result+'\n')

