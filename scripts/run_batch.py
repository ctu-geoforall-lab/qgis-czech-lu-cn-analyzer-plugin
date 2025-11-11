#!/usr/bin/env python3

import os
import sys
import argparse
import requests

sys.path.insert(0, "/usr/share/qgis/python/plugins")
from qgis.core import QgsApplication, QgsVectorLayer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from WFSdownloader import WFSDownloader
from PluginUtils import get_string_from_yaml

config_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))),
    "config"
)

def message(msg):
    print(msg, file=sys.stderr)

def wfs_downloader(polygon_layer):
    wfs_downloader = WFSDownloader(os.path.join(config_path, "layers_merging_order.csv"),
                                   True, polygon_layer, False)
    layer_list = wfs_downloader.get_ZABAGED_layers_list()

    # Load the URL from the ZABAGED.yaml file    
    ZABAGED_URL = get_string_from_yaml(
        os.path.join(config_path, "ZABAGED.yaml"), "URL"
    )

    # Get extent of the polygon layer
    ymin, xmin, ymax, xmax, extent = wfs_downloader.get_wfs_info(layer_list)

    ZABAGED_layers = []
    # Download ZABAGED layers from the WFS service
    message("Downloading ZABAGED...")
    for layer in layer_list:
        ZABAGED_layers.append(
            wfs_downloader.process_wfs_layer(
                layer, ymin, xmin, ymax, xmax, extent, ZABAGED_URL)
        )

    # Download LPIS
    lpis_config = os.path.join(config_path, "LPIS.yaml")
    LPIS_layername = get_string_from_yaml(lpis_config, "layer_name")
    LPIS_URL = get_string_from_yaml(lpis_config, "URL")
 
    message("Downloading LPIS...")   
    response = requests.get(LPIS_URL)
    
if __name__ == "__main__":
    # Initialize QGIS application in the main thread
    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    parser = argparse.ArgumentParser(
        description="Run computation in batch process."
    )

    parser.add_argument(
        "aoi",
        type=str,
        help="AOI polygon"
    )

    args = parser.parse_args()

    if not os.path.isfile(args.aoi):
        print(f"Chyba: Soubor '{args.aoi}' neexistuje.")
        sys.exit(1)

    layer_name = "testing_polygon"
    # Load the polygon GeoPackage layer
    polygon_layer = QgsVectorLayer(
        f"{args.aoi}|layername={layer_name}", layer_name, "ogr"
    )

    wfs_downloader(polygon_layer)
    
    del polygon_layer
    # Exit QGIS application
    qgs.exitQgis()

    
