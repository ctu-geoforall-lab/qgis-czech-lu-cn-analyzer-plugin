"""
This file focuses on downloading the LPIS data.
"""
from typing import Type

from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject, QgsField, QgsVectorDataProvider, QgsMessageLog, Qgis
from PyQt5.QtCore import QVariant
import yaml


from .function import process_wfs_layer, ClipByPolygon
from .layereditor import attribute_layer_edit


def GetLPISLayer(LPISURL: str, layer_name: str, LPISconfigpath: str, ymin: float, xmin: float, ymax: float, xmax:
float, current_extent: QgsGeometry, polygon: QgsVectorLayer, AreaFlag: bool, LayerList: list) -> list:

    """
    Downloads and processes an LPIS layer, optionally clips it by a polygon, and returns updated list of layers.
    """

    LPISlayer = process_wfs_layer(layer_name, ymin, xmin, ymax, xmax, current_extent, LPISURL)

    if LPISlayer is None:
        QgsMessageLog.logMessage("Unavailable LPIS Layer", "CzLandUseCN",level=Qgis.Warning, notifyUser=True)
        return LayerList

    # Set LPIS layer name to "LPIS_layer"
    LPISlayer.setName("LPIS_layer")

    return LayerList
