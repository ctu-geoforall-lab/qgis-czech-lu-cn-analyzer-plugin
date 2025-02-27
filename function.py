import os
from csv import excel

import processing
import yaml
from typing import Optional, List, Tuple, Union

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsGeometry,
    QgsFeature,
    QgsRasterLayer,
    QgsField,
    QgsVectorLayerUtils,
    QgsProcessingFeatureSourceDefinition,
    QgsMessageLog,
    Qgis
)
from qgis.utils import iface

from .layereditor import *

# WARNING: This script only works with EPSG:5514

def get_ZABAGED_layers_list(config_path: str) -> List[str]:
    """ Load WFS layers from the configuration file"""

    try:
        with open(config_path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()

        processed_lines = [line.strip() for line in lines if line.strip() != "LPIS_layer"]
        return processed_lines
    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to load WFS layers (layers_merging_order.csv): {e}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
        return []


def clip_layer(layer: QgsVectorLayer, extent: QgsRectangle, layer_name: str) -> QgsVectorLayer:
    """ Clip the layer to the given extent"""

    extent_geom = QgsGeometry.fromRect(extent)
    clipped_layer = QgsVectorLayer(
        f"{QgsWkbTypes.displayString(layer.wkbType())}?crs={layer.crs().authid()}",
        layer_name,
        "memory"
    )

    clipped_layer.dataProvider().addAttributes(layer.fields())
    clipped_layer.updateFields()

    for feature in layer.getFeatures(QgsFeatureRequest().setFilterRect(extent)):
        geom = feature.geometry()
        if geom.intersects(extent_geom):
            clipped_feature = QgsFeature()
            clipped_feature.setGeometry(geom.intersection(extent_geom))
            clipped_feature.setAttributes(feature.attributes())
            clipped_layer.dataProvider().addFeature(clipped_feature)

    clipped_layer.commitChanges()

    return clipped_layer


def get_wfs_info(use_polygon, wfs_layers, polygon=None):
    """ Get WFS layers and extent information"""

    if not wfs_layers:
        QgsMessageLog.logMessage("Corupted WFS setting, see config file","CzLandUseCN",
                                 level=Qgis.Warning, notifyUser=True)
        return

    if not use_polygon:
        extent = iface.mapCanvas().extent()
    elif polygon and polygon.isValid():
        extent = polygon.extent()
    else:
        QgsMessageLog.logMessage("Invalid polygon layer!", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)


    return extent.yMinimum(), extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent

def get_string_from_yaml(path: str, key: str) -> Optional[str]:
    """ Get a string from a YAML file"""
    try:
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
            return config.get(key)
    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to load {key} from {path}: {e}","CzLandUseCN",
                                 level=Qgis.Warning, notifyUser=True)
        return None

def getOneLineConfig(path: str) -> Optional[str]:
    """
    Get the configuration from a file with only one line. and skip comments.
    Used for URLs and other one-line configurations.
    """
    with open(path, 'r') as file:
        lines = [line for line in file if not line.startswith('#')]
        return lines[0].strip()


def process_wfs_layer(layer_name: str, ymin: float, xmin: float, ymax: float, xmax: float, extent: QgsGeometry,
                      URL: str) -> Optional[QgsVectorLayer]:
    """ Load and clip a WFS layer to the given extent"""

    uri = (
        f"{URL}?"
        f"&version=2.0.0&request=GetFeature&typename={layer_name}"
        f"&bbox={xmin},{ymin},{xmax},{ymax},EPSG:5514"
    )

    vlayer = QgsVectorLayer(uri, f"Layer: {layer_name}", "WFS")
    if not vlayer.isValid() or not vlayer.featureCount() or vlayer is None:
        QgsMessageLog.logMessage(f"Failed to load or empty layer: {layer_name}","CzLandUseCN",
                                 level=Qgis.Warning, notifyUser=True)
        return

    clipped_layer = clip_layer(vlayer, extent, layer_name)
    if clipped_layer.isValid():
        return clipped_layer


def ClipByPolygon(layer: QgsVectorLayer, polygon: QgsVectorLayer) -> QgsVectorLayer:
    params = {
        'INPUT': layer,
        'OVERLAY': polygon,
        'OUTPUT': 'memory:'
    }
    clipped_result = processing.run("native:clip", params)
    final_clipped_layer = clipped_result['OUTPUT']

    # Add the clipped layer to the map if it contains features
    if final_clipped_layer and final_clipped_layer.featureCount() > 0:
        final_clipped_layer.setName(layer.name())
        return final_clipped_layer # Return the clipped layer

def add_LPIS_LandUse_code(layer: QgsVectorLayer, LPIS_path: str) -> None:
    """Add LandUse code to LPIS layer based on its attributes."""
    try:
        with open(LPIS_path, 'r') as file:
            config = yaml.safe_load(file)
            lpis_layer_config = next((layer for layer in config['layers'] if layer['name'] == 'LPIS_layer'), None)
            if not lpis_layer_config:
                QgsMessageLog.logMessage("LPIS layer configuration not found in YAML.", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
                return

            base_use_code = lpis_layer_config['base_use_code']
            controlling_attribute = lpis_layer_config['controlling_attribute']
            value_increments = lpis_layer_config['value_increments']

            layer.startEditing()
            for feature in layer.getFeatures():
                attribute_value = feature[controlling_attribute]
                increment = value_increments.get(attribute_value, 0)
                feature["LandUse_code"] = base_use_code + increment
                layer.updateFeature(feature)
            layer.commitChanges()

    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to add LandUse code to LPIS layer: {e}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)



def add_landuse_attribute(layers: list, attribute_template_path: str, LPIS_path: str) -> list:
    """Add LandUse attribute to layers with the common string."""
    updated_layers = []

    for layer in layers:
        layer_name = layer.name()
        data_provider = layer.dataProvider()
        data_provider.addAttributes([QgsField("LandUse_code", QVariant.Int)])
        layer.updateFields()

        if layer_name == "LPIS_layer":
            # Skip LPIS layer
            add_LPIS_LandUse_code(layer,LPIS_path)
            continue

        with open(attribute_template_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")  # Use comma as the delimiter
                names = parts[:-1]  # All but the last value are names
                code = int(parts[-1])  # Last value is the code

                if any(name.lower() in layer_name.lower() for name in names):
                    layer.startEditing()
                    for feature in layer.getFeatures():
                        feature["LandUse_code"] = code
                        layer.updateFeature(feature)
                    layer.commitChanges()

            updated_layers.append(layer)  # Always append the layer

    return updated_layers

def buffer_layers(layers: list, buffer_config_path: str) -> list:
    """Buffer layers based on the configuration in the YAML file."""
    new_layers = []

    try:
        with open(buffer_config_path, 'r') as file:
            config = yaml.safe_load(file)
            buffer_layers_config = config.get('buffer_layers', [])

            for layer in layers:
                for layer_config in buffer_layers_config:
                    if layer.name() == layer_config.get('input_layer_name', ''):

                        buffered_layer = attribute_layer_buffer(
                            layer,
                            controlling_atr_name=layer_config['controlling_atr_name'],
                            default_buffer=layer_config['default_buffer'],
                            priorities=[b['priority'] for b in layer_config['buffer_levels']],
                            values=[b['values'] for b in layer_config['buffer_levels']],
                            distances=[b['distance'] for b in layer_config['buffer_levels']],
                            input_layer_name=layer_config['input_layer_name']
                        )
                        if buffered_layer:
                            QgsMessageLog.logMessage("Successful buffering: " + layer.name(), "CzLandUseCN",
                                                     level=Qgis.Info, notifyUser=False)
                            new_layers.append(buffered_layer)
                        else:
                            new_layers.append(layer)  # Keep original if buffering fails
                        break
                else:
                    new_layers.append(layer)  # If no config matches, keep the original

    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to buffer layers: {e}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
        new_layers.extend(layers)  # Keep original layers if error occurs

    return new_layers


def edit_landuse_code(layers: list, ATR_config_path: str) -> list:
    """Edit ZABAGED layers LandUse code by its attributes."""
    new_layers = []

    for layer in layers:
        try:
            with open(ATR_config_path, 'r') as ATRfile:
                ATRconfig = yaml.safe_load(ATRfile)

                for layer_config in ATRconfig['layers']:
                    if layer.name() == layer_config.get('name', ''):
                        edited_layer = attribute_layer_edit(
                            layer,
                            base_use_code=layer_config['base_use_code'],
                            controlling_attribute=layer_config['controlling_attribute'],
                            value_increments=layer_config['value_increments']
                        )
                        if edited_layer:
                            new_layers.append(edited_layer)
                            QgsMessageLog.logMessage("LandUse code attribute edit at: " + layer.name(), "CzLandUseCN",
                                                     level=Qgis.Info, notifyUser=False)
                        else:
                            new_layers.append(layer)  # Keep original if editing fails
                            QgsMessageLog.logMessage(f"/ERROR/ Layer {layer.name()} trashed.", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
                        break
                    else:
                        new_layers.append(layer)  # If no match, keep original


        except Exception as e:
            QgsMessageLog.logMessage(f"Failed to edit layer {layer.name()}: {e}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
            new_layers.append(layer)  # Keep original if error occurs

    return new_layers

def clip_layers_after_edits(layers: list, AreaFlag: bool,
                            polygon: Optional[QgsVectorLayer], ymin: float, xmin: float, ymax: float,
                            xmax: float) -> list:
    """
    Clip all layers in list to the given extent or polygon.
    Ensures the number of layers in the output matches the input.
    """

    clipped_layers = []

    for layer in layers:
        layer_name = layer.name()
        clipped_layer = None

        if not AreaFlag:  # Clip by extent
            extent = QgsRectangle(xmin, ymin, xmax, ymax)
            clipped_layer = clip_layer(layer, extent, f"{layer_name}")

        else:  # Clip by polygon
            if polygon:
                clipped_layer = ClipByPolygon(layer, polygon)

        # Ensure clipped layer is valid, else keep the original
        if clipped_layer and clipped_layer.isValid():
            clipped_layers.append(clipped_layer)
        else:
            QgsMessageLog.logMessage(f"Warning: Clipping failed for {layer_name}, keeping original.","CzLandUseCN",
                                     level=Qgis.Warning, notifyUser=True)
            clipped_layers.append(layer)  # Keep original if clipping fails

    return clipped_layers

def apply_symbology(layer: QgsVectorLayer, symbology_path: str) -> None:
    """Apply symbology to the layer from the specified file."""
    if not layer.isValid():
        QgsMessageLog.logMessage("Invalid layer for symbology", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
        return

    # Load the symbology from the file
    success = layer.loadSldStyle(symbology_path)
    if not success:
        QgsMessageLog.logMessage("Failed to load symbology", "CzLandUseCN",  level=Qgis.Warning, notifyUser=True)
        return





def stack_layers(qgs_project: QgsProject, layers: list, stacking_template_path: str) -> None:
    """
    Merge polygon layers by their priority from the stacking list - layers_merging_order.conf
    Also removes original input layers
    """

    # Function to merge layers
    def merge_layers(level_layers: List[QgsVectorLayer], output_name: str) -> Optional[QgsVectorLayer]:
        if len(level_layers) > 0:
            merged_layer = processing.run(
                "native:mergevectorlayers",
                {'LAYERS': level_layers, 'CRS': level_layers[0].crs(), 'OUTPUT': 'memory:'}
            )['OUTPUT']
            merged_layer.setName(output_name)
            QgsProject.instance().addMapLayer(merged_layer)  # Add merged layer to the project
            return merged_layer
        return None

    with open(stacking_template_path, 'r') as STCfile:
        # Read lines in order and put them in a list
        STClines = STCfile.readlines()
        STClist = [line.strip() for line in STClines]

        LayerOrderedList = []

        for layer in layers:
            # Only process vector layers and polygons
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 2:
                layer_name = layer.name()


                # Check if the layer is in the stacking list
                if layer_name in STClist:
                    LayerOrderedList.append(layer)
                else:
                    QgsMessageLog.logMessage(f"Layer '{layer_name}' not found in the stacking list.","CzLandUseCN",
                                                level=Qgis.Warning, notifyUser=True)
                    continue

        # Order layers by STClist, filtering only layers found in STClist
        LayerOrderedList = sorted(LayerOrderedList, key=lambda x: STClist.index(x.name()))

        # Merge each layer in order and stack by priority level
        priority_merged_layers = []
        for idx, layer in enumerate(LayerOrderedList):
            merged_layer = merge_layers([layer], f"Merged_Layer_Priority_{idx + 1}")
            if merged_layer:
                priority_merged_layers.append(merged_layer)

        # Reverse the list to merge the layers in the correct order
        priority_merged_layers.reverse()
        # Merge all priority layers together in the specified order
        final_merged_layer = merge_layers(priority_merged_layers, "LandUse_Layer")

        # Apply symbology to the merged layer
        path_to_sld = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colortables", "landuse.sld")
        apply_symbology(final_merged_layer, path_to_sld)
        final_merged_layer.triggerRepaint()

        # Add the final merged layer to the project
        if final_merged_layer:
            QgsProject.instance().addMapLayer(final_merged_layer)
        else:
            QgsMessageLog.logMessage("Failed to merge layers.","CzLandUseCN", level=Qgis.Critical, notifyUser=True)

        # Remove partial Marged_Layer layers
        for layer in priority_merged_layers:
            QgsProject.instance().removeMapLayer(layer.id())

        QgsMessageLog.logMessage("Stacking layers completed.", "CzLandUseCN", level=Qgis.Info, notifyUser=False)
        return None



