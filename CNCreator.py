import csv
from typing import Optional, Dict, List

from PyQt5.QtGui import QColor
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsWkbTypes,
    QgsStyle,
    QgsGraduatedSymbolRenderer,
    QgsSymbol,
    QgsRendererRange,
    QgsClassificationQuantile,
    QgsFields,
    QgsRuleBasedRenderer,
    QgsExpression
)
from PyQt5.QtCore import QVariant, Qt

def add_CN3_from_CN2(vector_layer: QgsVectorLayer, field_name: str) -> None:
    """Adds a new field 'CN3' to the vector layer, calculated from the 'CN2' field."""
    try:
        # Check if CN2 field exists
        if vector_layer.fields().indexOf(field_name) == -1:
            raise Exception(f"Field '{field_name}' not found in the layer.")

        # Add CN3 field if it doesn't exist
        if vector_layer.fields().indexOf("CN3") == -1:
            vector_layer.dataProvider().addAttributes([QgsField("CN3", QVariant.Double)])
            vector_layer.updateFields()

        # Calculate CN3 from CN2
        for feature in vector_layer.getFeatures():
            cn2_value = feature[field_name]
            if cn2_value is not None:
                cn3_value = 23 * cn2_value / (10 + 0.13 * cn2_value)
                feature["CN3"] = cn3_value
                vector_layer.updateFeature(feature)

    except Exception as e:
        raise Exception(f"Failed to calculate CN3: {e}")

def prune_cn_layer_fields(layer: QgsVectorLayer):
    """
    Deletes all attributes from the given layer except:
    Shape_Area, SHAPE_Area, OBJECTID, fid_zbg, FID, Shape_Length, LandUse_code, HSG.
    """
    # List of fields to keep
    keep_fields = [
        'Shape_Area', 'SHAPE_Area', 'OBJECTID',
        'fid_zbg', 'FID', 'Shape_Length',
        'source','LandUse_code', 'HSG'
    ]

    provider = layer.dataProvider()
    fields = provider.fields()

    # Determine indices of fields to delete
    delete_ids = []
    for field in fields:
        if field.name() not in keep_fields:
            delete_ids.append(fields.indexOf(field.name()))

    if delete_ids:
        provider.deleteAttributes(delete_ids)
        layer.updateFields()

def add_cn_symbology(vector_layer, field_name, symbology_path, ramp_name):
    """Applies symbology using a quantile-based color ramp for numeric features,
       and red for features with non-numeric (or NULL) values.
       Works by computing quantile breaks for the numeric values in the specified field.
       Then rule-based symbology is applied to the layer.
       (Color ramps do not show NULL values, so we need to handle them separately.)
    """
    try:
        # Load the style database.
        style = QgsStyle.defaultStyle()
        if not style.importXml(symbology_path):
            raise Exception(f"Failed to import symbology from path: {symbology_path}")

        # Get the color ramp named ramp_name
        color_ramp = style.colorRamp(ramp_name)
        if color_ramp is None:
            raise Exception("Color ramp 'CN' not found in the style database.")

        # Obtain the default symbol for this layer's geometry.
        base_symbol = QgsSymbol.defaultSymbol(vector_layer.geometryType())
        if base_symbol is None:
            raise Exception("Failed to create a default symbol for the vector layer geometry.")

        # Verify that field exists.
        if vector_layer.fields().indexOf(field_name) == -1:
            raise Exception(f"Field '{field_name}' not found in the layer.")

        # Collect numeric values from features.
        numeric_values = []
        for feat in vector_layer.getFeatures():
            val = feat[field_name]
            try:
                num = float(val)
                numeric_values.append(num)
            except (TypeError, ValueError):
                continue

        # If no numeric values exist, use a simple red symbol for all features.
        if not numeric_values:
            red_symbol = base_symbol.clone()
            red_symbol.setColor(QColor('red'))
            vector_layer.setRenderer(QgsRuleBasedRenderer(red_symbol))
            vector_layer.triggerRepaint()
            return

        # Calculate quantile breaks.
        min_value = min(numeric_values)
        max_value = max(numeric_values)
        num_classes = 15
        step = (max_value - min_value) / num_classes if max_value != min_value else 1

        rules = []
        for i in range(num_classes):
            lower = min_value + i * step
            if i < num_classes - 1:
                upper = lower + step
                # Expression using field name directly.
                expr_str = f'"{field_name}" >= {lower} AND "{field_name}" < {upper}'
                label = f"{lower:.2f} - {upper:.2f}"
            else:
                expr_str = f'"{field_name}" >= {lower} AND "{field_name}" <= {max_value}'
                label = f"{lower:.2f} - {max_value:.2f}"

            symbol = base_symbol.clone()
            # Get the color for this class.
            color = color_ramp.color(float(i) / (num_classes - 1))
            symbol.setColor(color)
            # Create the rule. Note the parameter order:
            # (symbol, maximumScale, minimumScale, filterExpression, label, description, elseRule)
            rule = QgsRuleBasedRenderer.Rule(symbol, 0, 0, expr_str, label, "", False)
            rules.append(rule)

        # Create a fallback rule as ELSE.
        fallback_symbol = base_symbol.clone()
        fallback_symbol.setColor(QColor('red'))
        # Setting elseRule=True means this rule applies to all features not matching prior rules.
        fallback_rule = QgsRuleBasedRenderer.Rule(fallback_symbol, 0, 0, '', 'Non-numeric', "", True)

        # Build the rule hierarchy.
        root_rule = QgsRuleBasedRenderer.Rule(None, 0, 0, '', 'Root', "", False)
        for rule in rules:
            root_rule.appendChild(rule)
        root_rule.appendChild(fallback_rule)

        # Create and set the rule-based renderer.
        renderer = QgsRuleBasedRenderer(root_rule)
        vector_layer.setRenderer(renderer)
        vector_layer.triggerRepaint()

    except Exception as e:
        raise Exception(f"Failed to apply rule-based symbology: {e}")

class CNCreatorError(Exception):
    """Custom exception for CNCreator errors."""
    pass

def _calculate_cn_value(feature: QgsFeature, cn_dict: Dict[int, List[float]]) -> Optional[float]:
    """Calculates the CN value for a given feature based on the CN dictionary."""
    landuse_val = feature["LandUse_code"]
    hsg_val = feature["HSG"]

    # pass None if the values are not present
    if landuse_val is None or hsg_val is None or landuse_val == "NULL" or hsg_val == "NULL":
        return None

    try:
        # Convert values to integers
        landuse = int(landuse_val)
        hsg = int(hsg_val)
    except (ValueError, TypeError):
        return None

    if hsg == 0:  # HSG 0 == water body
        return 99

    if landuse in cn_dict and 1 <= hsg <= 4:
        return cn_dict[landuse][hsg - 1]
    return None


class CNCreator:
    def __init__(self, IntLayer: QgsVectorLayer, CN_table_path: str) -> None:
        self.IntLayer: QgsVectorLayer = IntLayer
        self.CN_table_path: str = CN_table_path
        self.CNLayer: Optional[QgsVectorLayer] = None

    def CreateCNLayer(self) -> QgsVectorLayer:
        """Creates a CN layer from the input layer and CN table."""
        try:


            cn_dict = self._load_cn_table()
            new_layer = self._create_memory_layer()

            self._copy_features_with_cn(new_layer, cn_dict)

            new_layer.updateExtents()
            self.CNLayer = new_layer
            return self.CNLayer

        except Exception as e:
            raise CNCreatorError(f"Failed to create CN layer: {e}")

    def _load_cn_table(self) -> Dict[int, List[float]]:
        """Loads the CN table CSV into a dictionary."""
        cn_dict: Dict[int, List[float]] = {}
        with open(self.CN_table_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    try:
                        int(row[0])
                    except ValueError:
                        continue  # skip header

                landuse = int(row[0])
                cn_values = list(map(float, row[1:]))
                cn_dict[landuse] = cn_values
        return cn_dict

    def _create_memory_layer(self) -> QgsVectorLayer:
        """Creates a new memory layer with same fields as IntLayer and an additional CN field."""
        new_fields: QgsFields = self.IntLayer.fields()
        if new_fields.indexOf("CN2") == -1:
            new_fields.append(QgsField("CN2", QVariant.Double))

        if new_fields.indexOf("CN3") == -1:
            new_fields.append(QgsField("CN3", QVariant.Double))

        geometry_type = QgsWkbTypes.displayString(self.IntLayer.wkbType())
        crs = self.IntLayer.crs().authid()
        new_layer = QgsVectorLayer(f"{geometry_type}?crs={crs}", "CN_Layer", "memory")
        new_layer_data = new_layer.dataProvider()
        new_layer_data.addAttributes(new_fields)
        new_layer.updateFields()
        return new_layer

    def _copy_features_with_cn(self, new_layer: QgsVectorLayer, cn_dict: Dict[int, List[float]]) -> None:
        """Copies features from the input layer to the new layer with CN values calculated."""
        new_fields: QgsFields = new_layer.fields()
        new_layer_data = new_layer.dataProvider()

        for feature in self.IntLayer.getFeatures():
            new_feat = QgsFeature(new_fields)
            new_feat.setGeometry(feature.geometry())
            attrs = feature.attributes()

            try:
                # Calculate CN2
                cn_val = _calculate_cn_value(feature, cn_dict)
                if cn_val is not None:
                    # Calculate CN3 from CN2
                    cn3_val = 23 * cn_val / (10 + 0.13 * cn_val)
                else:
                    cn3_val = None
            except Exception as inner_e:
                raise CNCreatorError(f"Error processing feature ID {feature.id()}: {inner_e}")

            # Add CN2 and CN3 to attributes
            if new_fields.indexOf("CN2") == len(attrs):
                attrs.append(cn_val)
            else:
                attrs[new_fields.indexOf("CN2")] = cn_val

            if new_fields.indexOf("CN3") == len(attrs):
                attrs.append(cn3_val)
            else:
                attrs[new_fields.indexOf("CN3")] = cn3_val

            new_feat.setAttributes(attrs)
            new_layer_data.addFeature(new_feat)