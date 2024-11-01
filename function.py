import os
import processing

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


def get_current_polygon(polygon_layer):
    """ Retrieve points from the current polygon layer"""
    points = []
    for feature in polygon_layer.getFeatures():
        geom = feature.geometry()
        if geom.isGeosValid() and geom.type() == QgsWkbTypes.PolygonGeometry:
            points.extend(geom.asPolygon()[0])
    return points


def get_current_extent():
    """ Retrieve the current extent of the map canvas"""
    return iface.mapCanvas().extent()


def clip_layer(layer, extent, layer_name):
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


def load_zabaged_layers():
    """ Load WFS layers from the configuration file"""
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "zabagedlayers.conf")
    try:
        with open(config_path, "r") as file:
            return [line.strip() for line in file]
    except Exception as e:
        print(f"Failed to load WFS layers: {e}")
        return []


def get_wfs_info(use_polygon, polygon=None):
    """ Get WFS layers and extent information"""
    wfs_layers = load_zabaged_layers()
    if not wfs_layers:
        return "ERR_missingconffile", 0, 0, 0, 0, None  # return error code for later handling

    if not use_polygon:
        extent = get_current_extent()
    elif polygon and polygon.isValid():
        extent = polygon.extent()
    else:
        print("Invalid polygon layer")
        return "ERR_plg", 0, 0, 0, 0, None  # return error code for later handling

    return wfs_layers, extent.yMinimum(), extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent


def process_wfs_layer(layer_name, ymin, xmin, ymax, xmax, extent):
    """ Load and clip a WFS layer to the given extent"""
    uri = (
        f"https://ags.cuzk.cz/arcgis/services/ZABAGED_POLOHOPIS/MapServer/WFSServer?"
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


def load_raster_layer(extent):
    """ Load raster layer from WMS service """
    wms_uri = (
        f"contextualWMSLegend=0&crs=EPSG:5514&dpiMode=7&format=image/png&"
        f"layers=DPB_KUL&styles=&url=https://mze.gov.cz/public/app/wms/public_DPB_PB_OPV.fcgi&"
        f"tilePixelRatio=0&bbox={extent.xMinimum()},{extent.yMinimum()},{extent.xMaximum()},{extent.yMaximum()}"
    )

    rlayer = QgsRasterLayer(wms_uri, 'Raster Layer', 'wms')
    if rlayer.isValid():
        QgsProject.instance().addMapLayer(rlayer)
        print("Successfully loaded raster layer")
        return rlayer
    else:
        print("Failed to load raster layer")
        return None


def common_prefix(lines):
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


def get_common_string():
    """ Get the common string part for each line in zabaged.conf file"""
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "zabagedlayers.conf")
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

def add_attribute_to_layers(common_string, qgs_project):
    """ Add an attribute to all layers with the common string"""
    layers = qgs_project.values()
    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            layer.dataProvider().addAttributes([QgsField("LandUse_code", QVariant.Int)])
            layer.updateFields()

            attribute_template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "zabaged_to_LandUseCode_table.conf")
            with open(attribute_template_path, "r") as file:
                for line in file:
                    # split line by ; to get all names but don use the last one
                    names = line.split(";")[:-2]
                    # save the last one as the code ( [-1] is "\n" )
                    code = int(line.split(";")[-2])

                    if any(name.lower() in layer_name.lower() for name in names):

                        layer.startEditing()
                        for feature in layer.getFeatures():
                            feature["LandUse_code"] = code
                            layer.updateFeature(feature)
                        layer.commitChanges()

            # Add more specific code for the categorized forest layer by druh_k attribute
            if "les" in layer_name.lower() and "kategor" in layer_name.lower():
                forest_layer_edit(layer)

            if "silnice" in layer_name.lower() and "dálnice" in layer_name.lower():
                road_layer_edit(layer, common_string)

def clip_layers_with_common_string(common_string, qgs_project, AreaFlag, polygon, ymin, xmin, ymax, xmax):
    """ Clip all layers with the common string to the given extent or polygon """
    layers = qgs_project.values()
    for layer in layers:
        layer_name = layer.name()
        if common_string in layer_name:
            clipped_layer = None  # Initialize clipped_layer to None
            if not AreaFlag:  # Clip by extent
                extent = QgsRectangle(xmin, ymin, xmax, ymax)
                clipped_layer = clip_layer(layer, extent, f"{layer_name}_clipped")
            else:  # Clip by polygon
                if polygon:
                    extent = polygon.extent()
                    clipped_layer = clip_layer(layer, extent, f"{layer_name}_clipped")
                    clipped_layer = clip_layer_by_polygon(clipped_layer, polygon, f"{layer_name}_clipped_by_polygon")

            if clipped_layer and clipped_layer.isValid():
                QgsProject.instance().addMapLayer(clipped_layer)
                QgsProject.instance().removeMapLayer(layer.id())  # Remove the original unclipped layer
                print(f"Successfully clipped and removed original layer: {layer_name}")
            else:
                print(f"Failed to clip layer: {layer_name}")

def clip_layer_by_polygon(layer, polygon, layer_name):
    """ Clip the layer to the given polygon """
    clipped_layer = QgsVectorLayer(
        f"{QgsWkbTypes.displayString(layer.wkbType())}?crs={layer.crs().authid()}",
        layer_name,
        "memory"
    )

    clipped_layer.dataProvider().addAttributes(layer.fields())
    clipped_layer.updateFields()

    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom.intersects(polygon.geometry()):
            clipped_feature = QgsFeature()
            clipped_feature.setGeometry(geom.intersection(polygon.geometry()))
            clipped_feature.setAttributes(feature.attributes())
            clipped_layer.dataProvider().addFeature(clipped_feature)

    clipped_layer.commitChanges()
    if not clipped_layer.featureCount():
        print("No features added to the clipped layer.")

    return clipped_layer

def stack_layers(qgs_project,common_string):
    """
    Merge polygon layers by their priority:
    1) roads and paths
    2) water bodies and streams
    3) buildings
    4) LPIS
    5) other ZABAGED layers

    Also removes original input layers
    """
    lvl1_layer = []
    lvl2_layer = []
    lvl3_layer = []
    lvl4_layer = []
    lvl5_layer = []

    layers = qgs_project.mapLayers().values()
    for layer in layers:
        # Only process vector layers and polygons
        if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 2:
            layer_name = layer.name()

            if common_string in layer_name or "LPIS" in layer_name:

                # 1) roads and paths
                if any(substring in layer_name for substring in
                       ["Silnice", "Pěšina", "Cesta", "Ulice", "Most", "Lávka", "Parkoviště", "trať", "Koleiště",
                        "Tramvajová", "točna"]):
                    lvl1_layer.append(layer)

                # 2) water bodies and streams
                elif any(substring in layer_name for substring in ["tok", "Vodní_plocha"]):
                    lvl2_layer.append(layer)

                # 3) buildings
                elif any(substring in layer_name for substring in
                         ["Budova", "Věž", "Kůlna", "věž", "zásobní", "Silo", "Vodojem", "Větrný", "Rozvalina",
                          "Hradba", "Zeď", "Hrad", "Zámek", "stavba", "Tribuna", "Stavební", "zastávka",
                          "Stožár", "Elektrárna"]):
                    lvl3_layer.append(layer)

                # 4) LPIS
                elif "LPIS" in layer_name:
                    lvl4_layer.append(layer)

                # 5) other ZABAGED layers
                else:
                    lvl5_layer.append(layer)

    # Function to merge layers at each level
    def merge_layers(level_layers, output_name):
        if len(level_layers) > 0:
            merged_layer = processing.run(
                "native:mergevectorlayers",
                {'LAYERS': level_layers, 'CRS': level_layers[0].crs(), 'OUTPUT': 'memory:'}
            )['OUTPUT']
            merged_layer.setName(output_name)
            return merged_layer
        return None

    # Merge layers by priority level
    merged_lvl1 = merge_layers(lvl1_layer, "Merged_LVL1")
    merged_lvl2 = merge_layers(lvl2_layer, "Merged_LVL2")
    merged_lvl3 = merge_layers(lvl3_layer, "Merged_LVL3")
    merged_lvl4 = merge_layers(lvl4_layer, "Merged_LVL4")
    merged_lvl5 = merge_layers(lvl5_layer, "Merged_LVL5")

    # Combine merged levels into a final stacked layer
    final_merged_layers = [layer for layer in [merged_lvl5, merged_lvl4, merged_lvl3, merged_lvl2, merged_lvl1] if
                           layer]

    # Create final merged layer if there are any layers to merge
    if final_merged_layers:
        final_merged = processing.run(
            "native:mergevectorlayers",
            {'LAYERS': final_merged_layers, 'CRS': final_merged_layers[0].crs(), 'OUTPUT': 'memory:'}
        )['OUTPUT']
        final_merged.setName("Final_Merged_Layers")
        qgs_project.addMapLayer(final_merged)

    # Remove original layers after merging
    for layer in layers:
        layer_name = layer.name()
        if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 2 and (common_string in layer_name or "LPIS" in layer_name):
            QgsProject.instance().removeMapLayer(layer.id())

    print("Layers merged by priority with Final_Merged_Layers stacked by level.")
    return None
