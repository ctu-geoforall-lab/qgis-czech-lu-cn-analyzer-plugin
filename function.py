import os
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
    QgsProcessingFeatureSourceDefinition

)
from qgis.utils import iface

from .layereditor import *

# WARNING: This script only works with EPSG:5514

def get_ZABAGED_layers_list(config_path: str) -> List[str]:
    """ Load WFS layers from the configuration file"""

    try:
        with open(config_path, "r") as file:
            return [line.strip() for line in file]
    except Exception as e:
        print(f"Failed to load WFS layers: {e}")
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
    if not clipped_layer.featureCount():
        print("No features added to the clipped layer.")

    return clipped_layer


def get_wfs_info(use_polygon, wfs_layers, polygon=None):
    """ Get WFS layers and extent information"""

    if not wfs_layers:
        return "ERR_missingconffile", 0, 0, 0, 0, None  # return error code for later handling

    if not use_polygon:
        extent = iface.mapCanvas().extent()
    elif polygon and polygon.isValid():
        extent = polygon.extent()
    else:
        print("Invalid polygon layer")
        return "ERR_plg", 0, 0, 0, 0, None  # return error code for later handling

    return extent.yMinimum(), extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent


def load_one_line_config(file_name: str) -> Optional[str]:
    """Helper function to load a configuration file."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", file_name)
        return getOneLineConfig(config_path)
    except Exception as e:
        print(f"Failed to load configuration file {file_name}: {e}")
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
    if not vlayer.isValid() or not vlayer.featureCount():
        print(f"Failed to load or empty layer: {layer_name}")
        return None

    clipped_layer = clip_layer(vlayer, extent, layer_name)
    if clipped_layer.isValid():
        print(f"Successfully clipped layer: {layer_name}, feature count: {clipped_layer.featureCount()}")
        return clipped_layer


def ClipByPolygon(layer: QgsVectorLayer, polygon: QgsVectorLayer) -> None:
    print("Clipping layer to polygon...")
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
        QgsProject.instance().addMapLayer(final_clipped_layer)
        print(
            f"Added clipped layer: {final_clipped_layer.name()}, feature count: {final_clipped_layer.featureCount()}")


def common_prefix(lines: List[str]) -> str:
    """ Find the common prefix for a list of strings"""
    if not lines:
        return ""

    # Take the first line as the reference
    prefix = lines[0].strip()

    # Compare the prefix with each subsequent line
    for line in lines[1:]:
        line = line.strip()  # remove any surrounding whitespace or newline
        i = 0
        while i < len(prefix) and i < len(line) and prefix[i] == line[i]:
            i += 1
        # Shorten the prefix to the common part found
        prefix = prefix[:i]

        # If the prefix becomes empty, stop early
        if not prefix:
            break

    return prefix


def get_common_string(config_path) -> str:
    """ Get the common string part for each line in zabaged.conf file"""

    try:
        with open(config_path, "r") as file:
            lines = file.readlines()
            if not lines:
                return "conf_file_err"
            # Get the common string part from all lines
            common_part = common_prefix(lines)
            return common_part if common_part else "no_common_prefix"
    except Exception as e:
        return f"conf_file_err: {str(e)}"


def add_landuse_attribute(common_string: str, qgs_project: QgsProject, attribute_template_path: str) -> None:
    """Add LandUse attribute to layers with the common string."""
    # Retrieve all map layers in the project
    layers = qgs_project.mapLayers().values()

    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            # Add a new attribute "LandUse_code" of type integer
            data_provider = layer.dataProvider()
            data_provider.addAttributes([QgsField("LandUse_code", QVariant.Int)])
            layer.updateFields()

            # Open the template file and read attributes to update features
            with open(attribute_template_path, "r") as file:
                for line in file:
                    # Process template lines
                    names = line.split(";")[:-2]
                    code = int(line.split(";")[-2])

                    # Check if any name matches the layer name
                    if any(name.lower() in layer_name.lower() for name in names):
                        layer.startEditing()
                        for feature in layer.getFeatures():
                            feature["LandUse_code"] = code
                            layer.updateFeature(feature)
                        layer.commitChanges()


def buffer_layers(common_string: str, qgs_project: QgsProject, BUF_config_path: str) -> None:
    """Buffer line layers based on configuration."""
    # Retrieve all map layers in the project
    layers = qgs_project.mapLayers().values()

    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            try:
                with open(BUF_config_path, 'r') as BUFfile:
                    BUFconfig = yaml.safe_load(BUFfile)

                    for layer_config in BUFconfig['buffer_layers']:
                        default_buffer = layer_config['default_buffer']
                        buffer_levels = layer_config['buffer_levels']
                        controlling_atr_name = layer_config['controlling_atr_name']
                        input_layer_name = layer_config['input_layer_name']

                        priorities = []
                        values = []
                        distances = []
                        for buffer_level in buffer_levels:
                            priorities.append(buffer_level['priority'])
                            values.append(buffer_level['values'])
                            distances.append(buffer_level['distance'])

                        if input_layer_name == layer_name:
                            attribute_layer_buffer(
                                layer,
                                controlling_atr_name=controlling_atr_name,
                                default_buffer=default_buffer,
                                priorities=priorities,
                                values=values,
                                distances=distances,
                                input_layer_name=input_layer_name
                            )
            except Exception as e:
                print(f"Failed to buffer layer attributes: {e}")
                print("Please check the zabaged_atr_to_Buffer.yaml file for errors!")


def edit_landuse_code(common_string: str, qgs_project: QgsProject, ATR_config_path: str) -> None:
    """Edit ZABAGED layers LandUse code by its attributes."""
    # Retrieve all map layers in the project
    layers = qgs_project.mapLayers().values()

    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            try:
                with open(ATR_config_path, 'r') as ATRfile:
                    ATRconfig = yaml.safe_load(ATRfile)

                    for layer_config in ATRconfig['layers']:
                        base_use_code = layer_config['base_use_code']
                        controlling_attribute = layer_config['controlling_attribute']
                        value_increments = layer_config['value_increments']

                        attribute_layer_edit(
                            layer,
                            base_use_code=base_use_code,
                            controlling_attribute=controlling_attribute,
                            value_increments=value_increments
                        )
            except Exception as e:
                print(f"Failed to edit layer attributes: {e}")
                print("Please check the zabaged_atr_to_LandUse.yaml file for errors!")


def clip_layers_with_common_string(common_string: str, qgs_project: QgsProject, AreaFlag: bool,
                                   polygon: Optional[QgsVectorLayer], ymin: float, xmin: float, ymax: float,
                                   xmax: float) -> None:
    """
    (Used to clip final layers after buffering.)
    Clip all layers with the common string to the given extent or polygon.
    Remove the original layers after clipping.
    """
    layers = qgs_project.values()
    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            clipped_layer = None  # Initialize clipped_layer to None
            if not AreaFlag:  # Clip by extent
                extent = QgsRectangle(xmin, ymin, xmax, ymax)
                clipped_layer = clip_layer(layer, extent, f"{layer_name}")
            else:  # Clip by polygon
                if polygon:
                    extent = polygon.extent()
                    clipped_layer = clip_layer(layer, extent, f"{layer_name}")
                    clipped_layer = clip_layer_by_polygon(clipped_layer, polygon, f"{layer_name}")

            if clipped_layer and clipped_layer.isValid():
                QgsProject.instance().addMapLayer(clipped_layer)
                QgsProject.instance().removeMapLayer(layer.id())  # Remove the original unclipped layer
                print(f"Successfully clipped and removed original layer: {layer_name}")
            else:
                print(f"Failed to clip layer: {layer_name}")


def clip_layer_by_polygon(layer: QgsVectorLayer, polygon: QgsVectorLayer, layer_name: str) -> QgsVectorLayer:
    """Clip the layer to the given polygon."""
    clipped_layer = QgsVectorLayer(
        f"{QgsWkbTypes.displayString(layer.wkbType())}?crs={layer.crs().authid()}",
        layer_name,
        "memory"
    )

    clipped_layer.dataProvider().addAttributes(layer.fields())
    clipped_layer.updateFields()

    # Get the geometry of the polygon layer's first feature
    polygon_geom = None
    for poly_feature in polygon.getFeatures():
        polygon_geom = poly_feature.geometry()
        break  # Assuming a single polygon feature

    if not polygon_geom:
        print("Polygon geometry not found!")
        return clipped_layer

    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom.intersects(polygon_geom):
            clipped_feature = QgsFeature()
            clipped_feature.setGeometry(geom.intersection(polygon_geom))
            clipped_feature.setAttributes(feature.attributes())
            clipped_layer.dataProvider().addFeature(clipped_feature)

    clipped_layer.commitChanges()
    if not clipped_layer.featureCount():
        print("No features added to the clipped layer.")

    return clipped_layer


def stack_layers(qgs_project: QgsProject, common_string: str, stacking_template_path: str) -> None:
    """
    Merge polygon layers by their priority from the stacking list - layers_merging_order.conf
    Also removes original input layers
    """

    print("--- Merging polygon layers ---")

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
        # Skip first line and read others in order and put them in a list
        STClines = STCfile.readlines()[1:]
        STClist = [line.strip() for line in STClines]
        print(f"Ordering layers by priority: {STClist} - editable in layers_merging_order.conf")

        layers = qgs_project.mapLayers().values()
        LayerOrderedList = []

        for layer in layers:
            # Only process vector layers and polygons
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 2:
                layer_name = layer.name()

                if common_string in layer_name or "LPIS" in layer_name:
                    # Check if the layer is in the stacking list
                    if layer_name in STClist:
                        LayerOrderedList.append(layer)
                    else:
                        print(f"Layer '{layer_name}' not found in the stacking list.")
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

        # Add the final merged layer to the project
        if final_merged_layer:
            QgsProject.instance().addMapLayer(final_merged_layer)
        else:
            print("Failed to merge layers.")

        # Remove partial Marged_Layer layers
        for layer in priority_merged_layers:
            QgsProject.instance().removeMapLayer(layer.id())

        # Remove original layers after merging
        for layer in layers:
            layer_name = layer.name()
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 2 and (
                    common_string in layer_name or "LPIS" in layer_name):
                QgsProject.instance().removeMapLayer(layer.id())

        print("Layers merged by priority and added to the project as Final_Merged_Layer.")
        return None
