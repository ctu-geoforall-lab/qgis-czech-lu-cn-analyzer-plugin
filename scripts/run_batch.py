#!/usr/bin/env python3

import os
import sys
import argparse
import requests
import yaml

from PyQt5.QtCore import QVariant

sys.path.insert(0, "/usr/share/qgis/python/plugins")
from qgis.core import QgsApplication, QgsVectorLayer, Qgis, QgsVectorFileWriter, QgsCoordinateTransformContext, QgsField
from processing.core.Processing import Processing

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from WFSdownloader import WFSDownloader
from SoilDownloader import simple_clip
from LayerEditor import dissolve_polygon, buffer_QgsVectorLayer, add_constant_atr, merge_layers, apply_simple_difference
from WFStask import TASK_process_wfs_layer
from LayerEditorTask import TASK_edit_layers
from SoilTask import TASK_process_soil_layer
from IntersectionTask import TASK_Intersection
from InputChecker import is_valid_cn_csv
from CNtask import TASK_CN
from RunOffTask import TASK_RunOff

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
CN_table = os.path.join(config_path, "CN_table.csv")
WPS_config = os.path.join(config_path, "WPS_config.yaml")

def message(msg):
    print(msg, file=sys.stderr)

def log_to_stderr(message, tag, level):
    if level >= Qgis.Critical:
        sys.stderr.write(f"[{tag}] {message}\n")
        sys.exit(1)

def read_config(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config

def save_layer(layer, output_path):
    # layer.startEditing()
    # layer.addAttribute(QgsField("ogc_fid", QVariant.Int))
    # fid_index = layer.fields().indexFromName("ogc_fid")
    # for i, feature in enumerate(layer.getFeatures(), start=1):
    #     print(feature.id(), fid_index, i)
    #     layer.changeAttributeValue(feature.id(), fid_index, i)
    # layer.commitChanges()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    name = layer.name().replace(' ', '_')
    gpkg_path = os.path.join(output_path, name + '.shp')

    options = QgsVectorFileWriter.SaveVectorOptions()
    # options.driverName = "GPKG"
    options.driverName = "Esri Shapefile"
    options.layerName = name
    #options.layerOptions = ["FID=ogc_fid"]

    error, _, _, error_message = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        gpkg_path,
        QgsCoordinateTransformContext(),
        options
    )

    if error != QgsVectorFileWriter.NoError:
        message(f"Error storing {layer.name()}: {error_message}")
        sys.exit(1)

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
        "config",
        type=str,
        help="YAML config"
    )

    args = parser.parse_args()

    args_config = read_config(args.config)
    if not os.path.isfile(args_config["download"]["aoi"]):
        print(f"Chyba: Soubor '{args_config["download"]["aoi"]}' neexistuje.")
        sys.exit(1)

    layer_name = "testing_polygon"
    # Load the polygon GeoPackage layer
    polygon_layer = QgsVectorLayer(
        f'{args_config["download"]["aoi"]}|layername={layer_name}', layer_name, "ogr"
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
    save_layer(merged_layer, args_config["output"]["path"])
    sys.exit(1)
    
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

    message("Compute CN...")
    if combined_layer.fields().indexFromName("HSG") == -1 or \
       combined_layer.fields().indexFromName("LandUse_code") == -1:
        QgsMessageLog.logMessage("Intersection layer does not contain HSG or LandUse_code attribute.",
                                 "CzLandUseCN", level=Qgis.Critical)

    if not os.path.exists(CN_table):
        QgsMessageLog.logMessage("CN table file does not exist.", "CzLandUseCN", level=Qgis.Critical)

    if not is_valid_cn_csv(CN_table):
        QgsMessageLog.logMessage("CN table file is not valid.", "CzLandUseCN", level=Qgis.Critical)
    
    task = TASK_CN(combined_layer, CN_table)
    task.run()
    CNLayer = task.CNLayer
    CNLayer.setName("CN Layer")

    message("Computing RunOff...")
    if CNLayer.isValid() is False or CNLayer.fields().indexFromName("CN2") == -1:
        QgsMessageLog.logMessage("CN layer is not valid.", "CzLandUseCN", level=Qgis.Critical)
        
    task = TASK_RunOff(CNLayer, args_config["runoff"]["return_periods"],
                       False, None,
                       args_config["runoff"]["coefficient"],
                       None, WPS_config)
    task.run()

    del SoilLayer
    del clipped_soil_layer
    del polygon_buffer_layer    
    del polygon_layer
    # Exit QGIS application
    qgs.exitQgis()

    
