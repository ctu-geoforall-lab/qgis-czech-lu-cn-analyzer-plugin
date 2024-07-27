from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeatureRequest,
    QgsVectorFileWriter,
    QgsWkbTypes,
    QgsRectangle,
    QgsGeometry,
    QgsFeature
)
from qgis.utils import iface

import os


# WARNING: This script works only with EPSG:5514

# Function to get the current polygon from the map canvas

def get_current_polygon(polygon_layer):
    # Initialize an empty list to hold all points from the polygon
    points = []

    # Iterate through the features in the layer
    for feature in polygon_layer.getFeatures():
        # Get the geometry of the feature
        geom = feature.geometry()

        # Check if the geometry is a polygon
        if geom.isGeosValid() and geom.type() == QgsWkbTypes.PolygonGeometry:
            # Extract the polygon's points
            for polygon in geom.asPolygon():
                points.extend(polygon)

    return points


# Function to get the current map canvas extent
def get_current_extent():
    canvas = iface.mapCanvas()
    extent = canvas.extent()
    return extent


# Function to clip a vector layer to the given extent
def clip_layer(layer, extent):
    # Convert the QgsRectangle to QgsGeometry (polygon)
    extent_geom = QgsGeometry.fromRect(extent)

    # Create a temporary memory layer for the clipped features
    clipped_layer = QgsVectorLayer(
        f"{QgsWkbTypes.displayString(layer.wkbType())}?crs={layer.crs().authid()}",
        "Clipped Layer",
        "memory"
    )

    clipped_layer_data_provider = clipped_layer.dataProvider()
    clipped_layer_data_provider.addAttributes(layer.fields())
    clipped_layer.updateFields()

    # Create a feature request to filter the features by the current extent
    request = QgsFeatureRequest().setFilterRect(extent)
    features = layer.getFeatures(request)

    # Add features that intersect with the extent to the clipped layer
    added_feature_count = 0
    for feature in features:
        geom = feature.geometry()
        if geom.intersects(extent_geom):
            clipped_feature = QgsFeature()
            clipped_feature.setGeometry(geom.intersection(extent_geom))
            clipped_feature.setAttributes(feature.attributes())
            clipped_layer_data_provider.addFeature(clipped_feature)
            added_feature_count += 1

    clipped_layer.commitChanges()

    if added_feature_count == 0:
        print("No features added to the clipped layer.")

    return clipped_layer


def loadZabagedLayers():
    # load wfs layers from zabagedlayers.conf stored in the same directory

    # Get direcotry of this script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Join the directory with the file name
    file_path = os.path.join(script_dir, "zabagedlayers.conf")
    layers = []

    with open(file_path, "r") as f:
        for line in f:
            layers.append(line.strip())
    return layers


def load_wfs_layers(FLAG, polygon):
    layer_list = []
    layer_name_list = []
    # List all available layers from the WFS service
    try:
        wfs_layers = loadZabagedLayers()
    except Exception as e:
        print(f"Failed to load WFS layers: {e}")
        return "ERR_missingconffile", 0

    # Directory to save temporary layers
    temp_dir = os.path.join(os.path.expanduser("~"), "qgis_temp_layers")
    os.makedirs(temp_dir, exist_ok=True)

    # Get the current extent from the map canvas
    if not FLAG:
        current_extent = get_current_extent()
        xmin, ymin, xmax, ymax = current_extent.xMinimum(), current_extent.yMinimum(), current_extent.xMaximum(), current_extent.yMaximum()
    else:
        #Zoom to the polygon
        if polygon.isValid() and polygon is not None:
            current_extent = polygon.extent()
            xmin, ymin, xmax, ymax = current_extent.xMinimum(), current_extent.yMinimum(), current_extent.xMaximum(), current_extent.yMaximum()
        else:
            print("Invalid polygon layer")
            return "ERR_plg", []

    for layer_name in wfs_layers:
        uri = (f"https://ags.cuzk.cz/arcgis/services/ZABAGED_POLOHOPIS/MapServer/WFSServer?"
               f"&version=2.0.0&request=GetFeature&typename={layer_name}"
               f"&bbox={xmin},{ymin},{xmax},{ymax},EPSG:5514")  # Note the EPSG code changed to 5514

        vlayer = QgsVectorLayer(uri, f"Layer: {layer_name}", "WFS")

        if not vlayer.isValid():
            print(f"Failed to load layer: {layer_name}")
            continue

        print(f"Successfully loaded layer: {layer_name}, feature count: {vlayer.featureCount()}")

        if vlayer.featureCount() == 0:
            continue

        # Clip the layer to the current extent
        clipped_layer = clip_layer(vlayer, current_extent)

        # Check if features were added
        clipped_layer_feature_count = clipped_layer.featureCount()
        print(f"Clipped layer feature count: {clipped_layer_feature_count}")

        if clipped_layer_feature_count == 0:
            print(f"No features in clipped layer: {layer_name}")
            continue

        if not clipped_layer.isValid():
            print(f"Failed to load clipped layer: {layer_name}")
        else:

            layer_list.append(clipped_layer)
            layer_name_list.append(layer_name)
            print(f"Successfully loaded clipped layer: {layer_name}, feature count: {clipped_layer_feature_count}")

    return layer_list, layer_name_list


if __name__ == "__main__":
    load_wfs_layers(False, None)
