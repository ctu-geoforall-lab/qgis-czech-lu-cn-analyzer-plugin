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
    QgsRectangle,
    Qgis,
    QgsMessageLog
)
from qgis.utils import iface
from PyQt5.QtCore import Qt


def attribute_layer_edit(layer: QgsVectorLayer, base_use_code: int,
                         controlling_attribute: str, value_increments: dict) -> QgsVectorLayer:
    """
    Edit the layer based on the controlling attribute
    Add a more specific code to the LandUse_code field based on attribute values
    set in the value_increments dictionary
    """

    if controlling_attribute not in layer.fields().names():
        QgsMessageLog.logMessage(f"Attribute '{controlling_attribute}' not found in layer fields.", "CzLandUseCN",
                                    level=Qgis.Warning)
        raise ValueError(f"Attribute '{controlling_attribute}' not found in layer fields.")

    layer.startEditing()
    i=0
    for feature in layer.getFeatures():
        i=i+1
        code = base_use_code

        # Check if the controlling attribute exists in this feature
        if controlling_attribute in feature.fields().names():
            value = feature[controlling_attribute]
            # Look up the increment in the value_increments dictionary
            increment = value_increments.get(value, 0)  # Default to 0 if value not found
            code += increment
            feature["LandUse_code"] = code

            # Update the feature with the new LandUse_code
            layer.updateFeature(feature)
        else:
            QgsMessageLog.logMessage(
                f"Attribute '{controlling_attribute}' missing for feature ID {feature.id()} in layer '{layer.name()}'.",
                "CzLandUseCN", level=Qgis.Warning)

    layer.commitChanges()
    return layer


def attribute_layer_buffer(layer: QgsVectorLayer, controlling_atr_name: str, default_buffer: float, priorities: list,
                           values: list, distances: list, input_layer_name: str) -> QgsVectorLayer:

    """
    Edit the line or point layer (layer)
    Buffer the features by their attribute (controlling_atr_name) values (values)
    Buffer distances (distances) are in same order as values
    Delete the original layer from the project
    If the attribute value is not in values, buffer by default_buffer
    """

    # Flatten the values list
    flat_values = [item for sublist in values for item in sublist]

    # Check if the attribute exists in the layer
    if controlling_atr_name not in layer.fields().names():
        QgsMessageLog.logMessage(f"Attribute '{controlling_atr_name}' not found in layer fields.", "CzLandUse&CN",
                                    level=Qgis.Warning)

        raise ValueError(f"Attribute '{controlling_atr_name}' not found in layer fields.")

    # Create a new memory layer to store the buffered features
    buffer_layer = QgsVectorLayer(f"Polygon?crs={layer.crs().authid()}", f"{input_layer_name}", "memory")
    buffer_layer.startEditing()
    buffer_layer.dataProvider().addAttributes(layer.fields())
    buffer_layer.updateFields()

    for feature in layer.getFeatures():
        value = feature[controlling_atr_name]
        if value in flat_values:
            index = flat_values.index(value)
            buffer_distance = distances[index // len(values[0])]
        else:
            buffer_distance = default_buffer

        # Buffer the feature
        geom = feature.geometry()
        if geom.wkbType() == 1 or geom.wkbType() == 4: # 1 = Point, 4 = Multipoint
            buffer = geom.buffer(buffer_distance, 5)
        elif geom.wkbType() == 2 or geom.wkbType() == 5: # 2 = LineString, 5 = MultiLineString
            buffer = geom.buffer(buffer_distance, 2)
        else:
            QgsMessageLog.logMessage(f"Unsupported geometry type for feature ID {feature.id()}",
                                    level=Qgis.Warning,
                                    notifyUser = True)
            continue

        # Create a new feature with the buffered geometry and add it to the buffer layer
        new_feature = QgsFeature()
        new_feature.setGeometry(buffer)
        new_feature.setAttributes(feature.attributes())
        if not buffer_layer.addFeature(new_feature):
            QgsMessageLog.logMessage(f"Failed to add feature ID {feature.id()} to the buffer layer.",
                                    level=Qgis.Warning,
                                    notifyUser = True)

    # Commit changes to the buffer layer and add it to the project
    if not buffer_layer.commitChanges():
        QgsMessageLog.logMessage("Failed to commit changes to the buffer layer.",
                                 level=Qgis.Warning,
                                    notifyUser = True)
    else:
        return buffer_layer


