import tempfile
import zipfile
from pathlib import Path
import os


from owslib.wps import WebProcessingService, monitorExecution

from qgis.core import QgsRasterLayer, QgsVectorLayer, QgsField, QgsMessageLog, Qgis
from qgis.PyQt.QtCore import QVariant
import processing

from qgis.core import (
    QgsRasterLayer, QgsVectorLayer, QgsField, QgsProject
)

from PyQt5.QtCore import QVariant, QMessageLogContext

import processing
import tempfile
import os


def simple_clip(input_layer, clip_by_layer):
    """Clip a QgsVector layer by different QgsVector layer"""
    # Check if the input layer is valid
    if not input_layer.isValid():
        raise ValueError("Invalid input layer")

    # Check if the clip by layer is valid
    if not clip_by_layer.isValid():
        raise ValueError("Invalid clip by layer")

    # Clip the input layer
    result = processing.run("native:clip", {
        'INPUT': input_layer,
        'OVERLAY': clip_by_layer,
        'OUTPUT': 'memory:'
    })

    # Return the clipped layer
    return result['OUTPUT']

def polygonize_raster(raster_layer: QgsRasterLayer) -> str:
    """Convert a QgsRasterLayer into a QgsVectorLayer, separating different pixel values into polygons."""

    # Ensure the raster layer is valid
    if not raster_layer.isValid():
        raise ValueError("Invalid raster layer")

    # Get raster source path
    raster_path = raster_layer.source()

    # Create an output memory layer
    vector_layer = QgsVectorLayer("Polygon?crs=" + raster_layer.crs().authid(), "Polygonized", "memory")
    vector_provider = vector_layer.dataProvider()

    # Add attribute field for raster values
    vector_provider.addAttributes([QgsField("HSG", QVariant.Int)])
    vector_layer.updateFields()

    # Run the polygonize process
    temp_output = tempfile.NamedTemporaryFile(suffix=".gpkg").name
    result = processing.run("gdal:polygonize", {
        'INPUT': raster_path,
        'BAND': 1,
        'FIELD': 'HSG',
        'EIGHT_CONNECTEDNESS': False,
        'OUTPUT': temp_output
    })

    # Return path to temporary file
    return temp_output

def load_tiff_from_zip(path_to_zip):
    """Load the first TIFF from a ZIP file and return a QgsRasterLayer."""
    if isinstance(path_to_zip, list):
        path_to_zip = path_to_zip[0]  # Use the first element if it's a list

    extract_path = os.path.splitext(path_to_zip)[0]  # Extract to a folder named after the ZIP (without extension)

    # Ensure the extraction directory exists
    os.makedirs(extract_path, exist_ok=True)

    # Extract the first TIFF file from the ZIP (expexted to be the only one)
    with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith('.tif'):
                extracted_tiff = zip_ref.extract(file_name, extract_path)
                raster_layer = QgsRasterLayer(extracted_tiff, os.path.basename(file_name))
                if raster_layer.isValid():
                    return raster_layer
                else:
                    QgsMessageLog.logMessage("Failed to load raster layer from ZIP", "CzLandUseCN", level=Qgis.Critical)
                    return None
    return None

class SoilDownloader:
    """Class to download soil data using a WPS service."""
    def __init__(self, url, xml_template,process_identifier, polygon_Soil, ymin_s, xmin_s, ymax_s, xmax_s):
        self.url = url
        self.xml_template = xml_template
        self.polygon_Soil = polygon_Soil
        self.process_identifier = process_identifier

        self.ymin_s, self.xmin_s, self.ymax_s, self.xmax_s = ymin_s, xmin_s, ymax_s, xmax_s

    def create_custom_xml(self):
        """Create a custom XML request for the WPS service. Uses the XML template file and polygon."""

        try:
            with open(self.xml_template, 'r', encoding='utf-8') as file:
                xml_content = file.read()

            # Replace bounding box values
            xml_content = xml_content.replace("{{ lowerCorner }}", f"{self.xmin_s} {self.ymin_s}")
            xml_content = xml_content.replace("{{ upperCorner }}", f"{self.xmax_s} {self.ymax_s}")

            # Extract coordinates and attributes from QgsVectorLayer
            features = self.polygon_Soil.getFeatures()
            coordinates_list = []
            attributes_list = []

            for feature in features:
                geom = feature.geometry()
                if geom.isMultipart():
                    polygons = geom.asMultiPolygon()
                else:
                    polygons = [geom.asPolygon()]

                for polygon in polygons:
                    coords = []
                    for point in polygon[0]:
                        coords.append(f"{point.x()},{point.y()}")
                    coordinates_list.append(" ".join(coords))

                # Extract attributes dynamically
                attributes_xml = ""
                for field in self.polygon_Soil.fields():
                    value = feature[field.name()]
                    attributes_xml += f"<ogr:{field.name()}>{value}</ogr:{field.name()}>"
                    attributes_list.append(attributes_xml)

                    # Replace coordinates and attributes
                    xml_content = xml_content.replace("{{ coordinates }}", " ".join(coordinates_list))
                    xml_content = xml_content.replace("{{ attributes }}", " ".join(attributes_list))

        except Exception as e:
            QgsMessageLog.logMessage(str(e), "CzLandUseCN", level=Qgis.Critical)
            raise Exception(f"Failed to create custom XML: {e}")



        return xml_content



    def execute_wps_request(self):
        """Execute the WPS request and download the output files."""
        # Initialize the WPS service
        QgsMessageLog.logMessage("Soil - Executing WPS request", "CzLandUseCN", level=Qgis.Info)
        try:
            wps = WebProcessingService(self.url)


            # Read the request from the XML file
            requestXML = self.create_custom_xml()


            # Execute the request
            execution = wps.execute(self.process_identifier, [], request=requestXML.encode('utf-8'))
            monitorExecution(execution)

            # Check if the process succeeded
            if execution.getStatus() != "ProcessSucceeded":
                raise Exception("WPS request failed: " + str(execution.errors))

            # Download the output files
            output_files = []
            for output in execution.processOutputs:
                ofile = str(Path(tempfile._get_default_tempdir()) / next(tempfile._get_candidate_names())) + '.zip'
                execution.getOutput(ofile, output.identifier)
                output_files.append(ofile)
        except Exception as e:
            QgsMessageLog.logMessage( str(e), "CzLandUseCN", level=Qgis.Critical)
            raise Exception(f"Failed to execute WPS request: {e}")

        return output_files

