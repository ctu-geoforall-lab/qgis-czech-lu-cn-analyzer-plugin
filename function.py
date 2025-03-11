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
from .WFSdownloader import  WFSDownloader
from .layereditor import *

# WARNING: This script only works with EPSG:5514

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

    wfs_downloader = WFSDownloader(None, AreaFlag, polygon)

    clipped_layers = []

    for layer in layers:
        layer_name = layer.name()
        clipped_layer = None

        if not AreaFlag:  # Clip by extent
            extent = QgsRectangle(xmin, ymin, xmax, ymax)
            clipped_layer = wfs_downloader.clip_layer(layer, extent, f"{layer_name}")

        else:  # Clip by polygon
            if polygon:
                clipped_layer = wfs_downloader.ClipByPolygon(layer)

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



