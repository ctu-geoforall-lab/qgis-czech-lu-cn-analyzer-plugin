#!/usr/bin/env python3

import os
import sys
import argparse

from qgis.core import QgsApplication, QgsVectorLayer

config_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))),
    "config", "layers_merging_order.csv"
)

def wfs_downloader():
    pass

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
    print(f"{args.aoi}|layername={layer_name}")
    polygon_layer = QgsVectorLayer(
        f"{args.aoi}|layername={layer_name}", layer_name, "ogr"
    )

    # Exit QGIS application
    qgs.exitQgis()

    
