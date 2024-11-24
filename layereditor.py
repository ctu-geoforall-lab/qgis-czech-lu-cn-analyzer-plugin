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


def attribute_layer_edit(layer: QgsVectorLayer, base_use_code: int,
                         controlling_attribute: str, value_increments: dict) -> None:
    """
    Edit the layer based on the controlling attribute
    Add a more specific code to the LandUse_code field based on attribute values
    set in the value_increments dictionary
    """
    if controlling_attribute not in layer.fields().names():
        return  # Exit the function if the attribute is missing

    layer.startEditing()
    for feature in layer.getFeatures():
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
            print(
                f"|zabaged_atr_to_LandUse.yaml| Warning: Attribute '{controlling_attribute}' missing for feature ID "
                f"{feature.id()} in layer '{layer.name()}'")

    layer.commitChanges()


def attribute_layer_buffer(layer: QgsVectorLayer, controlling_atr_name: str, default_buffer: float, priorities: list, values: list, distances: list, input_layer_name: str) -> None:

    """
    Edit the line or point layer (layer)
    Buffer the features by their attribute (controlling_atr_name) values (values)
    Buffer distances (distances) are in same order as values
    Delete the original layer from the project
    If the attribute value is not in values, buffer by default_buffer
    """
    print("---BUFFERING---")
    print(f"Layer: {layer.name()}")
    print(f"Controlling attribute: {controlling_atr_name}")

    print(f"set atributes names: {values}")
    print(f"atributes in layer: {layer.fields().names()}")

    print(f"Default buffer distance: {default_buffer}")
    print(f"Buffer distances: {distances}")

    # Flatten the values list
    flat_values = [item for sublist in values for item in sublist]

    # Check if the attribute exists in the layer
    if controlling_atr_name not in layer.fields().names():
        print(f"Attribute '{controlling_atr_name}' not found in layer fields.")
        print(f"Layer fields: {layer.fields().names()}")
        return  # Exit the function if the attribute is missing

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
        print(f"Feature ID {feature.id()} geometry type: {geom.wkbType()}")
        if geom.wkbType() == 1:
            buffer = geom.buffer(buffer_distance, 5)
        elif geom.wkbType() == 2:
            buffer = geom.buffer(buffer_distance, 2)
        else:
            print(f"Warning: Unsupported geometry type for feature ID {feature.id()} in layer '{layer.name()}'")
            continue

        # Create a new feature with the buffered geometry and add it to the buffer layer
        new_feature = QgsFeature()
        new_feature.setGeometry(buffer)
        new_feature.setAttributes(feature.attributes())
        if not buffer_layer.addFeature(new_feature):
            print(f"Failed to add buffered feature for feature ID {feature.id()}")

    # Commit changes to the buffer layer and add it to the project
    if not buffer_layer.commitChanges():
        print("Failed to commit changes to the buffer layer.")
    else:
        QgsProject.instance().addMapLayer(buffer_layer)
        print("Buffer layer added to the project.")

    # Remove the original input layer from the QGIS project
    QgsProject.instance().removeMapLayer(layer.id())
    print("Original layer removed from the project.")
    print("---BUFFERING COMPLETE---")
