import os

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
    QgsRectangle
)
from qgis.utils import iface
from PyQt5.QtCore import Qt

def forest_layer_edit(layer):
    """
    Edit the forest layer
    Add a more specific code to the LandUse_code field
    """
    layer.startEditing()
    for feature in layer.getFeatures():
        code = 30000
        value = feature["druh_k"]
        # non categorized forest
        if value == "N":
            feature["LandUse_code"] = code

        # coniferous forest
        elif value == "J":
            code += 3200
            feature["LandUse_code"] = code

        # deciduous forest
        elif value == "L":
            code += 3100
            feature["LandUse_code"] = code

        # mixed forest
        else:
            code += 3300
            feature["LandUse_code"] = code
        layer.updateFeature(feature)

    layer.commitChanges()

def road_layer_edit(layer, common):
    """
    Edit the road layer
    Buffer the roads by their typsil_k value
    Creates new buffer layer with the LandUse_code field
    """

    bufferLayerName = common + "_Silnice_buffer"

    # Create a new memory layer for the buffered geometries
    buffer_layer = QgsVectorLayer("Polygon?crs=EPSG:5514", bufferLayerName, "memory")
    buffer_layer_data_provider = buffer_layer.dataProvider()

    # Add the LandUse_code field to the new layer
    buffer_layer_data_provider.addAttributes([QgsField("LandUse_code", QVariant.Int)])
    buffer_layer.updateFields()

    # Start editing the original layer
    layer.startEditing()

    for feature in layer.getFeatures():
        # Set the code to 40000 for all roads
        code = 44100
        feature["LandUse_code"] = code

        if 'typsil_k' in feature.fields().names():
            value = feature["typsil_k"]
        else:
            print("ERROR: No typsil_k field!")
            continue

        geom = feature.geometry()

        # Buffer the road by the typsil_k value with flat ends
        if value in ["D1", "D2", "M", "D1p", "Mp", "Mv"]:
            buffer = geom.buffer(20, 1)
        elif value in ["S1", "S1v", "S1p"]:
            buffer = geom.buffer(12.5, 1)
        elif value in ["S2", "S3", "D2p", "S2p", "S2v", "S3p", "S3v"]:
            buffer = geom.buffer(12.5, 1)
        else:
            buffer = geom.buffer(7.5, 1)

        # Create a new feature for the buffer
        buffer_feature = QgsFeature(buffer_layer.fields())
        buffer_feature.setGeometry(buffer)
        buffer_feature["LandUse_code"] = code

        # Add the buffer feature to the new layer
        buffer_layer_data_provider.addFeature(buffer_feature)

        # Update the original feature
        feature.setGeometry(buffer)
        layer.updateFeature(feature)

    # Commit changes to the original layer
    layer.commitChanges()

    # Add the new buffer layer to the project
    QgsProject.instance().addMapLayer(buffer_layer)
