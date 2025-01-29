"""
This file focuses on downloading the LPIS data.
"""
from typing import Type

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject, QgsField, QgsVectorDataProvider
from PyQt5.QtCore import QVariant
import yaml


from .function import process_wfs_layer, ClipByPolygon
from .layereditor import attribute_layer_edit


def GetLPISLayer(LPISURL: str, layer_name: str, LPISLandUseCodes: str, ymin: float, xmin: float, ymax: float, xmax:
float, current_extent: QgsGeometry, polygon: QgsVectorLayer, AreaFlag: bool, LayerList: list) -> list:

    """
    Downloads and processes an LPIS layer, optionally clips it by a polygon, and returns updated list of layers.
    """

    LPISlayer = process_wfs_layer(layer_name, ymin, xmin, ymax, xmax, current_extent, LPISURL)

    if LPISlayer is None:
        print("Layer not found")
        return LayerList

    # Set LPIS layer name to "LPIS_layer"
    LPISlayer.setName("LPIS_layer")

    print("Updating LPIS layer...")
    # Add an empty LandUse_code attribute
    LPISlayer.dataProvider().addAttributes([QgsField("LandUse_code", QVariant.Int)])
    LPISlayer.updateFields()

    try:
        # Load the LandUseCodes from the YAML file
        with open(LPISLandUseCodes, 'r') as ATRfile:
            LPISconfig = yaml.safe_load(ATRfile)

        for layer_config in LPISconfig['layers']:
            # Extract parameters for each layer
            base_use_code = layer_config['base_use_code']
            controlling_attribute = layer_config['controlling_attribute']
            value_increments = layer_config['value_increments']

            # Edit the layer based on the controlling attribute
            attribute_layer_edit(LPISlayer, base_use_code, controlling_attribute, value_increments)

    except FileNotFoundError:
        print(f"Error: File not found --- possibly corrupted LPIS_atr_to_LandUse.yaml file")
        return LayerList

    except yaml.YAMLError as e:
        print(f"Error: YAML error --- {e}")
        return LayerList

    except Exception as e:
        print(f"Error: {e}")
        return LayerList

        # Clip the layer to the polygon if the AreaFlag is set
    if AreaFlag and polygon:
        # Clip the layer to the polygon
        ClipByPolygon(LPISlayer, polygon)
    else:
        # Add the unclipped layer to the map if it contains features based on the AreaFlag
        LayerList.append(LPISlayer)

    return LayerList
