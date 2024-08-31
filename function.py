import os
from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsGeometry,
    QgsFeature,
    QgsRasterLayer
)
from qgis.utils import iface


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


if __name__ == "__main__":
    print("This script is not meant to be run directly.")
