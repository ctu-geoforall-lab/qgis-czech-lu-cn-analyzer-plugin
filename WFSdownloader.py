from qgis.core import QgsMessageLog, Qgis, QgsVectorLayer, QgsRectangle, QgsGeometry, QgsFeature, QgsFeatureRequest, \
    QgsWkbTypes
from qgis.utils import iface
import processing
from typing import Optional, List


class WFSDownloaderError(Exception):
    pass


class WFSDownloader:
    """ Class to download and clip WFS layers, used before and during WFStask """

    def __init__(self, conf_path, area_flag, polygon, SoilFlag):
        self.config_path = conf_path
        self.AreaFlag = area_flag
        self.polygon = polygon
        self.SoilFlag = SoilFlag

    def get_ZABAGED_layers_list(self) -> List[str]:
        """ Load WFS layers from the configuration file"""
        try:
            with open(self.config_path, mode='r', encoding='utf-8') as file:
                lines = file.readlines()

            processed_lines = [line.strip() for line in lines if line.strip() != "LPIS_layer"]
            return processed_lines
        except Exception as e:
            QgsMessageLog.logMessage(f"Failed to load WFS layers (layers_merging_order.csv): {e}", "CzLandUseCN",
                                     level=Qgis.Warning, notifyUser=True)
            return []

    def clip_layer(self, layer: QgsVectorLayer, extent: QgsRectangle, layer_name: str) -> QgsVectorLayer:
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

        return clipped_layer

    def get_wfs_info(self, wfs_layers):
        """ Get WFS layers and extent information"""
        if not wfs_layers:
            QgsMessageLog.logMessage("Corupted WFS setting, see config file", "CzLandUseCN",
                                     level=Qgis.Warning, notifyUser=True)
            return None

        if not self.AreaFlag:
            extent = iface.mapCanvas().extent()
        elif self.polygon and self.polygon.isValid() or self.SoilFlag:
            extent = self.polygon.extent()
        else:
            QgsMessageLog.logMessage("Invalid polygon layer!", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)

        return extent.yMinimum(), extent.xMinimum(), extent.yMaximum(), extent.xMaximum(), extent

    def process_wfs_layer(self, layer_name: str, ymin: float, xmin: float, ymax: float, xmax: float,
                          extent: QgsGeometry,URL: str) -> Optional[QgsVectorLayer]:
        """ Load and clip a WFS layer to the given extent"""
        uri = (
            f"{URL}?"
            f"version=2.0.0&request=GetFeature"
            f"&typename={layer_name}"
            f"&bbox={xmin},{ymin},{xmax},{ymax},EPSG:5514"
        )

        vlayer = QgsVectorLayer(uri, f"Layer: {layer_name}", "WFS")
        if not vlayer.isValid() or not vlayer.featureCount() or vlayer is None:
            QgsMessageLog.logMessage(f"Failed to load or empty layer: {layer_name}", "CzLandUseCN",
                                     level=Qgis.Warning, notifyUser=True)
            return None

        clipped_layer = self.clip_layer(vlayer, extent, layer_name)
        if clipped_layer.isValid():
            return clipped_layer
        return None

    def ClipByPolygon(self, layer: QgsVectorLayer) -> QgsVectorLayer:
        """ Clip the layer to the polygon extent"""
        params = {
            'INPUT': layer,
            'OVERLAY': self.polygon,
            'OUTPUT': 'memory:'
        }
        clipped_result = processing.run("native:clip", params)
        final_clipped_layer = clipped_result['OUTPUT']

        # Add the clipped layer to the map if it contains features
        if final_clipped_layer and final_clipped_layer.featureCount() > 0:
            final_clipped_layer.setName(layer.name())
            return final_clipped_layer  # Return the clipped layer
        return None

    def GetLPISLayer(self, LPISURL: str, layer_name: str, LPISconfigpath: str, ymin: float, xmin: float, ymax: float,
                     xmax: float, current_extent: QgsGeometry, LayerList: list) -> list:
        """ Get the LPIS layer from the WFS service"""
        wfs_downloader = WFSDownloader(LPISconfigpath, self.AreaFlag, self.polygon, self.SoilFlag)
        LPISlayer = wfs_downloader.process_wfs_layer(layer_name, ymin, xmin, ymax, xmax, current_extent, LPISURL)
        if LPISlayer is None:
            QgsMessageLog.logMessage("Unavailable LPIS Layer", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            return LayerList
        LPISlayer.setName("LPIS_layer")
        LayerList.append(LPISlayer)
        return LayerList