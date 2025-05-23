import os
import processing
from typing import Optional, List, Tuple
import yaml
from qgis.analysis import QgsNativeAlgorithms


from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeature,
    QgsField,
    QgsRectangle,
    Qgis,
    QgsMessageLog,
    QgsFields,
    QgsGeometry,
    QgsProcessingFeatureSourceDefinition,
    QgsWkbTypes
)

# Based on the environment, import the WFSdownloader/SoilDownloader module
try:
    from .WFSdownloader import WFSDownloader
except ImportError:
    from WFSdownloader import WFSDownloader
try:
    from .SoilDownloader import simple_clip
except ImportError:
    from SoilDownloader import simple_clip



def apply_simple_difference(layer1: QgsVectorLayer, layer2: QgsVectorLayer) -> QgsVectorLayer:
    """Apply a simple difference operation to the input layers."""

    diff = processing.run(
        "native:difference",
        {
            'INPUT': layer1,
            'OVERLAY': layer2,
            'OUTPUT': 'memory:'
        }
    )['OUTPUT']

    return diff


def add_constant_atr(layer, atr_name, atr_value):
    """Add a constant int attribute to the layer."""
    layer.dataProvider().addAttributes([QgsField(atr_name, QVariant.Int)])
    layer.updateFields()  # Update fields to reflect the changes
    layer.startEditing()
    for feature in layer.getFeatures():
        feature.setAttribute(atr_name, atr_value)
        layer.updateFeature(feature)
    layer.commitChanges()
    return layer


def dissolve_polygon(layer: QgsVectorLayer) -> QgsVectorLayer:
    """Dissolve the input polygon layer, keeping only an ID attribute with a value of 1.
    (for simple use cases)"""

    # Run dissolve without retaining any specific field
    dissolved_layer = processing.run(
        "native:dissolve",
        {
            'INPUT': layer,
            'FIELD': [],  # No fields retained initially
            'OUTPUT': 'memory:'
        }
    )['OUTPUT']

    # Get data provider
    provider = dissolved_layer.dataProvider()

    # Remove all existing attributes
    provider.deleteAttributes([i for i in range(len(provider.fields()))])
    dissolved_layer.updateFields()

    # Add a new 'ID' field
    provider.addAttributes([QgsField('ID', QVariant.Int)])
    dissolved_layer.updateFields()

    # Set 'ID' value to 1 for all features
    dissolved_layer.startEditing()
    for feature in dissolved_layer.getFeatures():
        feature.setAttribute('ID', 1)
        dissolved_layer.updateFeature(feature)
    dissolved_layer.commitChanges()

    return dissolved_layer

def dissolve_and_resolve_overlaps(input_layer: QgsVectorLayer, controlling_attribute: str) -> QgsVectorLayer:
    """
    Dissolves and de-overlaps features based on controlling_attribute.
    If the process yields no geometry, returns the original layer.
    """
    # Dissolve by attribute
    dissolved = processing.run(
        'native:dissolve',
        {'INPUT': input_layer, 'FIELD': [controlling_attribute], 'OUTPUT': 'memory:dissolved'}
    )['OUTPUT']

    # If dissolve produced nothing, return original
    if dissolved.featureCount() == 0:
        return input_layer

    # Preserve original layer name on the result
    dissolved.setName(input_layer.name())
    return dissolved

def resolve_overlaping_buffers(layers: list, config_path: str) -> list:
    """
    Reads YAML config, processes only named buffer layers, and returns a new list with those layers replaced by
    their de-overlapped versions (others unchanged).

    :param layers: List of QgsVectorLayer instances
    :param config_path: Path to YAML config with 'buffer_layers' entries containing 'input_layer_name'
    :return: New list of QgsVectorLayer with processed buffers
    """
    # Load configuration and extract layer names
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        to_process = {item.get('input_layer_name') for item in config.get('buffer_layers', [])}

    # Build new list, replacing only matching layers
    output_layers = []
    for lyr in layers:
        if lyr.name() in to_process:
            processed = dissolve_and_resolve_overlaps(lyr, 'LandUse_code')
            output_layers.append(processed)
        else:
            output_layers.append(lyr)

    return output_layers


def clip_larger_layer_to_smaller(layer_one: QgsVectorLayer, layer_two: QgsVectorLayer) -> Optional[Tuple[QgsVectorLayer, QgsVectorLayer]]:
    """" Determine which layer is larger and clip it to the extent of the smaller layer."""
    dissolved_layer_one = dissolve_polygon(layer_one)
    dissolved_layer_two = dissolve_polygon(layer_two) # Dissolve both layers

    # Get the area of the dissolved layers
    area_one = sum([feature.geometry().area() for feature in dissolved_layer_one.getFeatures()])
    area_two = sum([feature.geometry().area() for feature in dissolved_layer_two.getFeatures()])

    try:
        if area_one > area_two:
            clipped_layer_one = simple_clip(layer_one, dissolved_layer_two)
            QgsMessageLog.logMessage("Larger layer was cliped by smaller one.", "CzLandUseCN",
                                     level=Qgis.Info, notifyUser=False)
            return clipped_layer_one, layer_two

        elif area_two > area_one:
            clipped_layer_two = simple_clip(layer_two, dissolved_layer_one)
            QgsMessageLog.logMessage("Larger layer was cliped by smaller one.", "CzLandUseCN",
                                     level=Qgis.Info, notifyUser=False)
            return layer_one, clipped_layer_two

        else:
            QgsMessageLog.logMessage("Layers have the same area, no clipping needed.", "CzLandUseCN",
                                     level=Qgis.Info, notifyUser=False)

            return layer_one, layer_two

    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to clip layers: {e} - They have to overlap each other!",
                                 "CzLandUseCN", level=Qgis.Critical, notifyUser=True)
        return None

def get_polygon_from_extent(ymin: int, xmin: int, ymax: int, xmax: int) -> QgsVectorLayer:
    """Get a polygon from the extent."""
    rect = QgsRectangle(xmin, ymin, xmax, ymax)
    # Create QgsVectorLayer from the polygon
    layer = QgsVectorLayer("Polygon?crs=EPSG:5514", "Rectangle Layer", "memory")
    provider = layer.dataProvider()

    # Define attributes
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    provider.addAttributes(fields)
    layer.updateFields()

    # Create a feature with the rectangle geometry
    feature = QgsFeature()
    feature.setGeometry(QgsGeometry.fromRect(rect))
    feature.setAttributes([1])  # Assign an ID
    provider.addFeature(feature)

    # Refresh the layer
    layer.updateExtents()
    return layer

def buffer_QgsVectorLayer(input_layer, distance, segments=10):
    """
    Creates a buffered QgsVectorLayer from an input polygon layer.
    """

    # Create a memory layer to store buffered features
    buffer_layer = QgsVectorLayer("Polygon?crs=" + input_layer.crs().authid(),
                                  "BufferedLayer", "memory")
    provider = buffer_layer.dataProvider()

    # Copy attributes from input layer
    fields = input_layer.fields()
    provider.addAttributes(fields)
    buffer_layer.updateFields()

    # Process features
    for feature in input_layer.getFeatures():
        buffered_geom = feature.geometry().buffer(distance, segments)

        if buffered_geom.isEmpty():
            continue

        # Create new feature with the same attributes
        new_feature = QgsFeature()
        new_feature.setGeometry(buffered_geom)
        new_feature.setAttributes(feature.attributes())

        # Add feature to buffer layer
        provider.addFeature(new_feature)

    buffer_layer.updateExtents()

    return buffer_layer

def attribute_layer_edit(layer: QgsVectorLayer, base_use_code: int, controlling_attribute: str,
                         value_increments: dict) -> QgsVectorLayer:
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
            QgsMessageLog.logMessage(
                f"Attribute '{controlling_attribute}' missing for feature ID {feature.id()} in layer '{layer.name()}'.",
                "CzLandUseCN", level=Qgis.Warning)

    layer.commitChanges()
    return layer


def attribute_layer_buffer(layer: QgsVectorLayer, controlling_atr_name: str, default_buffer: float,
                           priorities: list,
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
        QgsMessageLog.logMessage(f"Attribute '{controlling_atr_name}' not found in layer fields.", "CzLandUseCN",
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
        if geom.wkbType() == 1 or geom.wkbType() == 4:  # 1 = Point, 4 = Multipoint
            buffer = geom.buffer(buffer_distance, 5)
        elif geom.wkbType() == 2 or geom.wkbType() == 5:  # 2 = LineString, 5 = MultiLineString
            buffer = geom.buffer(buffer_distance, 2)
        else:
            QgsMessageLog.logMessage(f"Unsupported geometry type for feature ID {feature.id()}",
                                     level=Qgis.Warning, notifyUser=True)
            continue

        # Create a new feature with the buffered geometry and add it to the buffer layer
        new_feature = QgsFeature()
        new_feature.setGeometry(buffer)
        new_feature.setAttributes(feature.attributes())
        if not buffer_layer.addFeature(new_feature):
            QgsMessageLog.logMessage(f"Failed to add feature ID {feature.id()} to the buffer layer.",
                                     level=Qgis.Warning, notifyUser=True)

    # Commit changes to the buffer layer and add it to the project
    if not buffer_layer.commitChanges():
        QgsMessageLog.logMessage("Failed to commit changes to the buffer layer.",
                                 level=Qgis.Warning, notifyUser=True)
        return None
    else:
        return buffer_layer

def apply_simple_buffer(layer: QgsVectorLayer, buffer_distance: float) -> QgsVectorLayer:
    """
    Apply a simple buffer to the input layer
    """

    # Create a new memory layer to store the buffered features
    buffer_layer = QgsVectorLayer(f"Polygon?crs={layer.crs().authid()}", f"{layer.name()}", "memory")
    buffer_layer.startEditing()
    buffer_layer.dataProvider().addAttributes(layer.fields())
    buffer_layer.updateFields()

    for feature in layer.getFeatures():
        geom = feature.geometry()
        if geom.wkbType() == 1 or geom.wkbType() == 4:  # 1 = Point, 4 = Multipoint
            buffer = geom.buffer(buffer_distance, 5)
        elif geom.wkbType() == 2 or geom.wkbType() == 5:  # 2 = LineString, 5 = MultiLineString
            buffer = geom.buffer(buffer_distance, 2)
        else:
            QgsMessageLog.logMessage(f"Unsupported geometry type for feature ID {feature.id()}",
                                     level=Qgis.Warning, notifyUser=True)
            continue

        # Create a new feature with the buffered geometry and add it to the buffer layer
        new_feature = QgsFeature()
        new_feature.setGeometry(buffer)
        new_feature.setAttributes(feature.attributes())
        if not buffer_layer.addFeature(new_feature):
            QgsMessageLog.logMessage(f"Failed to add feature ID {feature.id()} to the buffer layer.",
                                     level=Qgis.Warning, notifyUser=True)

    # Commit changes to the buffer layer and add it to the project
    if not buffer_layer.commitChanges():
        QgsMessageLog.logMessage("Failed to commit changes to the buffer layer.",
                                 level=Qgis.Warning, notifyUser=True)
        return None
    else:
        return buffer_layer


def merge_layers(level_layers: List[QgsVectorLayer], output_name: str) -> Optional[QgsVectorLayer]:
    """ Merge the layers in the list and return the merged layer. """
    if len(level_layers) > 0:
        merged_layer = processing.run(
            "native:mergevectorlayers",
            {'LAYERS': level_layers, 'CRS': level_layers[0].crs(), 'OUTPUT': 'memory:'}
        )['OUTPUT']
        merged_layer.setName(output_name)

        return merged_layer
    return None


class LayerEditor:
    """Class to edit layers based on the configuration files. Creates and modifies LandUse_code attribute. Layers are
    buffered and stacked based on the configuration files."""

    def __init__(self, at_path, LPIS_path, ZABAGED_path, st_path, symbol_path, AreaFlag, polygon, ymin, xmin, ymax, xmax):
        self.attribute_template_path = at_path
        self.LPIS_config_path = LPIS_path
        self.ZABAGED_config_path = ZABAGED_path
        self.stacking_template_path = st_path
        self.symbology_path = symbol_path
        self.AreaFlag = AreaFlag
        self.polygon = polygon
        self.ymin, self.xmin, self.ymax, self.xmax = ymin, xmin, ymax, xmax


    def add_LPIS_LandUse_code(self, layer: QgsVectorLayer) -> None:
        """Add LandUse code to LPIS layer based on its attributes."""
        try:
            with open(self.LPIS_config_path , 'r') as file:
                config = yaml.safe_load(file)
                # Get the LPIS layer configuration from the YAML file
                lpis_layer_config = next((layer for layer in config['layers'] if layer['name'] == 'LPIS_layer'), None)
                if not lpis_layer_config:
                    QgsMessageLog.logMessage("LPIS layer configuration not found in YAML.", "CzLandUseCN",
                                             level=Qgis.Warning, notifyUser=True)
                    return

                base_use_code = lpis_layer_config['base_use_code']
                controlling_attribute = lpis_layer_config['controlling_attribute']
                value_increments = lpis_layer_config['value_increments']

                # Check if the controlling attribute exists in the layer
                layer.startEditing()
                for feature in layer.getFeatures():
                    # Get the attribute value from the feature
                    attribute_value = feature[controlling_attribute]
                    # Look up the increment in the value_increments dictionary
                    increment = value_increments.get(attribute_value, 0)
                    # Calculate the LandUse code
                    feature["LandUse_code"] = base_use_code + increment
                    layer.updateFeature(feature)
                layer.commitChanges()

        except Exception as e:
            QgsMessageLog.logMessage(f"Failed to add LandUse code to LPIS layer: {e}", "CzLandUseCN",
                                     level=Qgis.Warning, notifyUser=True)

    def add_landuse_attribute(self, layers: list) -> list:
        """Add LandUse attribute to layers with the common string."""
        updated_layers = []

        for layer in layers:
            layer_name = layer.name()
            # add source layer name to the layer
            if layer.fields().indexFromName("source") == -1:
                layer.dataProvider().addAttributes([QgsField("source", QVariant.String)])
                layer.updateFields()
            layer.startEditing()
            for feature in layer.getFeatures():
                feature["source"] = layer_name
                layer.updateFeature(feature)
            layer.commitChanges()

            data_provider = layer.dataProvider()
            data_provider.addAttributes([QgsField("LandUse_code", QVariant.Int)])
            layer.updateFields()

            if layer_name == "LPIS_layer":
                # Skip LPIS layer
                self.add_LPIS_LandUse_code(layer)
                updated_layers.append(layer)
                continue

            with open(self.attribute_template_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)  # Load YAML data

                for entry in data["land_use"]:
                    names = entry["keywords"]  # Get keyword list
                    code = entry["code"]  # Get land use code

                    if any(name.lower() in layer_name.lower() for name in names):
                        layer.startEditing()
                        for feature in layer.getFeatures():
                            feature["LandUse_code"] = code
                            layer.updateFeature(feature)
                        layer.commitChanges()

                updated_layers.append(layer)  # Always append the layer

        return updated_layers

    def buffer_layers(self, layers: list) -> list:
        """Buffer layers based on the configuration in the YAML file."""
        new_layers = []

        try:
            with open(self.ZABAGED_config_path , 'r') as file:
                config = yaml.safe_load(file)
                buffer_layers_config = config.get('buffer_layers', [])

                for layer in layers: # Iterate over all layers
                    for layer_config in buffer_layers_config:
                        if layer.name() == layer_config.get('input_layer_name', ''):
                            if layer_config['controlling_atr_name'] == "NaN" or layer_config['controlling_atr_name'] == "None"  or layer_config['controlling_atr_name'] == "":
                                buffered_layer = apply_simple_buffer(layer, layer_config['default_buffer'])
                            else:
                                buffered_layer = attribute_layer_buffer(
                                    layer,
                                    controlling_atr_name=layer_config['controlling_atr_name'],
                                    default_buffer=layer_config['default_buffer'],
                                    priorities=[b['priority'] for b in layer_config['buffer_levels']],
                                    values=[b['values'] for b in layer_config['buffer_levels']],
                                    distances=[b['distance'] for b in layer_config['buffer_levels']],
                                    input_layer_name=layer_config['input_layer_name']
                                ) # Buffer the layer based on the config
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
            QgsMessageLog.logMessage(f"Failed to buffer layers: {e}", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            new_layers.extend(layers)  # Keep original layers if error occurs

        return new_layers

    def edit_landuse_code(self, layers: list) -> list:
        """Edit ZABAGED layers LandUse code by its attributes."""
        new_layers = []

        for layer in layers:  # Iterate over all layers
            try:
                with open(self.ZABAGED_config_path, 'r') as ATRfile:
                    ATRconfig = yaml.safe_load(ATRfile)

                    matched = False
                    for layer_config in ATRconfig['layers']:  # Iterate over all layers in the config
                        if layer.name() == layer_config.get('name', ''):
                            edited_layer = attribute_layer_edit(
                                layer,
                                base_use_code=layer_config['base_use_code'],
                                controlling_attribute=layer_config['controlling_attribute'],
                                value_increments=layer_config['value_increments']
                            )  # Edit the layer based on the config
                            if edited_layer:
                                new_layers.append(edited_layer)
                                QgsMessageLog.logMessage("LandUse code attribute edit at: " + layer.name(),
                                                         "CzLandUseCN",
                                                         level=Qgis.Info, notifyUser=False)
                            else:
                                new_layers.append(layer)  # Keep original if editing fails
                                QgsMessageLog.logMessage(f"/ERROR/ Layer {layer.name()} trashed.", "CzLandUseCN",
                                                         level=Qgis.Warning, notifyUser=True)
                            matched = True
                            break

                    if not matched:
                        new_layers.append(layer)  # If no match, keep original

            except Exception as e:
                QgsMessageLog.logMessage(f"Failed to edit layer {layer.name()}: {e}", "CzLandUseCN", level=Qgis.Warning,
                                         notifyUser=True)
                new_layers.append(layer)  # Keep original if error occurs

        return new_layers


    def clip_layers_after_edits(self, layers: list) -> list:
        """
        Clip all layers in list to the given extent or polygon.
        Ensures the number of layers in the output matches the input.
        (Used mainly after buffering)
        """

        wfs_downloader = WFSDownloader(None, self.AreaFlag, self.polygon, False)

        clipped_layers = []

        for layer in layers:
            layer_name = layer.name()
            clipped_layer = None

            if not self.AreaFlag:  # Clip by extent
                extent = QgsRectangle(self.xmin, self.ymin, self.xmax, self.ymax)
                clipped_layer = wfs_downloader.clip_layer(layer, extent, f"{layer_name}")

            else:  # Clip by polygon
                if self.polygon:
                    clipped_layer = wfs_downloader.ClipByPolygon(layer)

            # Ensure clipped layer is valid, else keep the original
            if clipped_layer and clipped_layer.isValid():
                clipped_layers.append(clipped_layer)
            else:
                QgsMessageLog.logMessage(f"Warning: Clipping failed for {layer_name}, keeping original.", "CzLandUseCN",
                                         level=Qgis.Warning, notifyUser=True)
                clipped_layers.append(layer)  # Keep original if clipping fails

        return clipped_layers

    def apply_symbology(self, layer: QgsVectorLayer) -> QgsVectorLayer:
        """Apply symbology to the layer from the specified file."""
        if not layer.isValid():
            QgsMessageLog.logMessage("Invalid layer for symbology", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
            return layer

        success = layer.loadSldStyle(self.symbology_path)
        if success:
            QgsMessageLog.logMessage("Symbology applied successfully", "CzLandUseCN", level=Qgis.Info)
        else:
            QgsMessageLog.logMessage("Failed to load symbology", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)

        return layer

    def stack_layers(self, layers: List[QgsVectorLayer]) -> Optional[QgsVectorLayer]:
        """
        Stack polygon layers by priority, clipping overlaps.
        Before each union, remove null/empty geometries, fix invalid ones,
        and (optionally) check validity to avoid 'Could not write feature' errors.
        """

        # 1) Read stacking order
        try:
            with open(self.stacking_template_path, 'r') as f:
                order = [ln.strip() for ln in f if ln.strip()]
        except Exception as e:
            QgsMessageLog.logMessage(f"Failed reading stacking template: {e}",
                                     "CzLandUseCN", level=Qgis.Critical)
            return None

        # 2) Filter & sort polygon layers (0=Point, 1=Line, 2=Polygon)
        ordered = [
            lyr for lyr in layers
            if isinstance(lyr, QgsVectorLayer)
               and lyr.geometryType() == 2
               and lyr.name() in order
        ]
        ordered.sort(key=lambda L: order.index(L.name()))
        if not ordered:
            QgsMessageLog.logMessage("No valid polygon layers to stack.",
                                     "CzLandUseCN", level=Qgis.Critical)
            return None

        processed = []
        accum_union = None

        for idx, lyr in enumerate(ordered):
            # A) First layer: clone to avoid altering source
            if idx == 0:
                clipped = lyr.clone()
            else:
                # B) Subtract higher-priority areas
                clipped = processing.run(
                    "native:difference",
                    {
                        'INPUT': lyr,
                        'OVERLAY': accum_union,
                        'OUTPUT': 'memory:clipped'
                    }
                )['OUTPUT']

            # C) Remove null & empty geometries (essential!)
            clipped = processing.run(
                "native:removenullgeometries",
                {'INPUT': clipped, 'OUTPUT': 'memory:clean_clipped'}
            )['OUTPUT']

            # E) Append for later merging (post-clean)
            processed.append(clipped)

            # F) Build/update running union
            if accum_union is None:
                accum_union = clipped.clone()
            else:
                # 1) Fix geometries on both sides
                fixed_acc = processing.run(
                    "native:fixgeometries",
                    {'INPUT': accum_union, 'OUTPUT': 'memory:fixed_acc'}
                )['OUTPUT']
                fixed_clip = processing.run(
                    "native:fixgeometries",
                    {'INPUT': clipped, 'OUTPUT': 'memory:fixed_clip'}
                )['OUTPUT']

                # 2) Finally union the clean, valid inputs
                try:
                    accum_union = processing.run(
                        "native:union",
                        {
                            'INPUT': fixed_acc,
                            'OVERLAY': fixed_clip,
                            'OUTPUT': 'memory:accum_union'
                        }
                    )['OUTPUT']

                except:
                    continue

            QgsMessageLog.logMessage(
                f"Layer '{lyr.name()}' processed ({idx + 1}/{len(ordered)})",
                "CzLandUseCN", level=Qgis.Info
            )

        # 4) Merge all non-overlapping pieces
        final = processing.run(
            "native:mergevectorlayers",
            {
                'LAYERS': processed,
                'CRS': processed[0].crs().toWkt(),
                'OUTPUT': 'memory:Stacked_NoOverlap'
            }
        )['OUTPUT']

        # 5) Style & add to project
        final = self.apply_symbology(final)
        final.setName("LandUse Layer")
        final.triggerRepaint()

        QgsMessageLog.logMessage("Stacking complete: no overlaps remain.",
                                 "CzLandUseCN", level=Qgis.Info)
        return final
