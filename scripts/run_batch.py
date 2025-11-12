#!/usr/bin/env python3

# TODO: cache qgis logs

import os
import sys
import argparse
import requests

sys.path.insert(0, "/usr/share/qgis/python/plugins")
from qgis.core import QgsApplication, QgsVectorLayer, Qgis
from processing.core.Processing import Processing

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from WFSdownloader import WFSDownloader
from SoilDownloader import simple_clip
from LayerEditor import dissolve_polygon, buffer_QgsVectorLayer, add_constant_atr, merge_layers, apply_simple_difference
from WFStask import TASK_process_wfs_layer
from LayerEditorTask import TASK_edit_layers
from SoilTask import TASK_process_soil_layer
from IntersectionTask import TASK_Intersection

config_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))),
    "config"
)
ZABAGED_config = os.path.join(config_path, "ZABAGED.yaml")
LPIS_config = os.path.join(config_path, "LPIS.yaml")
attribute_template = os.path.join(config_path, "zabaged_to_LandUseCode_table.yaml")
stacking_template = os.path.join(config_path,
                                 "layers_merging_order.csv")
lu_symbology = os.path.join(os.path.dirname(config_path), "colortables", "landuse.sld")
soil_symbology = os.path.join(os.path.dirname(config_path), "colortables", "soil.sld")
    
def message(msg):
    print(msg, file=sys.stderr)

def log_to_stderr(message, tag, level):
    if level >= Qgis.Critical:
        sys.stderr.write(f"[{tag}] {message}\n")

if __name__ == "__main__":
    # Initialize QGIS application in the main thread
    QgsApplication.setPrefixPath("/usr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    Processing.initialize()
    QgsApplication.messageLog().messageReceived.connect(log_to_stderr)

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

    # disslove the polygon layer for faster processing
    polygon_layer = dissolve_polygon(polygon_layer)

    message("Downloading ZABAGED and LPIS data...")
    wfs_downloader = WFSDownloader(os.path.join(config_path, "layers_merging_order.csv"),
                                   True, polygon_layer, True)
    wfs_layers = wfs_downloader.get_ZABAGED_layers_list()
    ymin, xmin, ymax, xmax, extent = wfs_downloader.get_wfs_info(wfs_layers)

    LandUseLayers = []
    task = TASK_process_wfs_layer(wfs_layers, ymin, xmin, ymax, xmax, extent,
                                  polygon_layer, True,
                                  None, None, None, None, None, None,
                                  LandUseLayers)
    task.run()
    
    message("Processing downloaded data...")   
    task = TASK_edit_layers(attribute_template, LPIS_config, ZABAGED_config, stacking_template,
                            lu_symbology, True, polygon_layer, ymin, xmin, ymax, xmax,
                            None, None, LandUseLayers)
    task.run()
    merged_layer = task.merged_layer
    
    message("Downloading soil data...")
    polygon_buffer_layer = buffer_QgsVectorLayer(polygon_layer, 25) # TODO: ymin?
    task = TASK_process_soil_layer(polygon_buffer_layer, ymin, xmin, ymax, xmax,
                                   extent, None, None, None, None)
    task.run()
    SoilLayer = QgsVectorLayer(task.polygoniziedLayer_Path, "Soil Layer", "ogr")
    # Clip the layer by polygon that is not buffered
    clipped_soil_layer = simple_clip(SoilLayer, polygon_layer)
    # Add HSG attribute to the area defining polygon and use it as underline layer for water bodies
    polygon_layer = add_constant_atr(polygon_layer, "HSG", 0)
    # Clip the water bodies layer to the polygon by the soil layer
    polygon_layer = apply_simple_difference(polygon_layer, clipped_soil_layer)
    # Merge the clipped soil layer with the polygon that is not buffered
    clipped_soil_layer = merge_layers([polygon_layer, clipped_soil_layer],"Soil Layer HSG")
    clipped_soil_layer.loadSldStyle(soil_symbology)

    message("Perform intersection...")
    task = TASK_Intersection(clipped_soil_layer, merged_layer,
                             None, None)
    task.run()
    combined_layer = task.combined_layer
    print(combined_layer)
    
    del SoilLayer
    del clipped_soil_layer
    del polygon_buffer_layer    
    del polygon_layer
    # Exit QGIS application
    qgs.exitQgis()

    
