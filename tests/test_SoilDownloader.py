# Ensure that qgis packages are imported to your python environment when running locally
# (/usr/lib/python3/dist-packages/qgis)

import pytest
import os
import sys

from osgeo import gdal
from qgis.core import QgsVectorLayer,  QgsRasterLayer

# Add the parent directory to the PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SoilDownloader import SoilDownloader, load_tiff_from_zip, polygonize_raster
from PluginUtils import get_string_from_yaml
from test_LayerEditor import check_layer_validity



def test_soil_downloader():
    """Test the SoilDownloader class."""

    config_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")

    # Mock parameters
    URL = get_string_from_yaml(os.path.join(config_folder, 'Soil.yaml'), "URL")
    XML_template = os.path.join(config_folder, 'Soil_template.xml')
    process_identifier = get_string_from_yaml(os.path.join(config_folder, 'Soil.yaml'), "process_identifier")

    # Load the polygon layer
    base_folder = os.path.dirname(__file__)
    input_folder = os.path.join(base_folder, 'input_files', "testing_LayerEditor_data")
    plg_path = os.path.join(input_folder, 'low.gpkg')
    polygon = QgsVectorLayer(f"{plg_path}|layername=low", "low", "ogr")

    # Ensure the polygon layer is valid
    assert check_layer_validity(polygon, "low", plg_path)
    print("[OK] Successfully loaded the polygon layer from input_files")

    ymin, xmin, ymax, xmax = (polygon.extent().yMinimum(), polygon.extent().xMinimum(),
                              polygon.extent().yMaximum(), polygon.extent().xMaximum())

    # Initialize the SoilDownloader
    soil_downloader = SoilDownloader(URL, XML_template, process_identifier, polygon, ymin, xmin, ymax, xmax)
    assert soil_downloader is not None, "Failed to initialize SoilDownloader"
    print("[OK] SoilDownloader initialized successfully")

    # Create custom XML
    custom_xml = soil_downloader.create_custom_xml()
    assert custom_xml is not None, "Failed to create custom XML"
    print("[OK] Custom XML created successfully")

    # Execute WPS request
    output_files = soil_downloader.execute_wps_request()
    assert output_files is not None, "Failed to execute WPS request"
    print("[OK] WPS request executed successfully")

    # Check if output files exist
    soil_raster = load_tiff_from_zip(output_files)
    assert soil_raster is not None and soil_raster.isValid(), "Failed to load raster from ZIP"
    print("[OK] Raster loaded successfully from ZIP")

    # Check if soil raster matches file in reference folder
    reference_folder = os.path.join(base_folder, 'reference')
    reference_raster_path = os.path.join(reference_folder, 'soil_reference.tif')
    assert os.path.exists(reference_raster_path), f"Reference raster not found at {reference_raster_path}"
    reference_raster = QgsRasterLayer(reference_raster_path, "soil_reference")
    assert reference_raster.isValid(), "Failed to load reference raster"
    print("[OK] Reference raster loaded successfully")

    # Compare rasters
    soil_raster_data = gdal.Open(soil_raster.source()).ReadAsArray()
    reference_raster_data = gdal.Open(reference_raster.source()).ReadAsArray()
    assert (soil_raster_data == reference_raster_data).all(), "Raster data does not match reference"
    print("[OK] Raster data matches reference raster")


