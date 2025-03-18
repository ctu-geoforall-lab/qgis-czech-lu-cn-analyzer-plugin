import pytest
import sys
import os
from qgis.core import QgsApplication, QgsVectorLayer
import requests

# Ensure that qgis packages are imported to your python environment when running locally
# (/usr/lib/python3/dist-packages/qgis)

# Add the parent directory to the PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WFSdownloader import WFSDownloader
from PluginUtils import get_string_from_yaml

# Initialize QGIS application in the main thread
qgs = QgsApplication([], False)
qgs.initQgis()

class TestWFSDownloader:
    """Test the WFSDownloader class"""
    @classmethod
    def teardown_class(cls):
        # Exit QGIS application
        qgs.exitQgis()

    def test_get_WFS_layers(self):
        """Test the WFSDownloader class to download WFS layers"""
        # Path to the polygon GeoPackage
        gpkg_path = os.path.join(os.path.dirname(__file__), 'input_files', 'testing_polygon.gpkg')
        layer_name = "testing_polygon"

        # Ensure the polygon GeoPackage file exists
        assert os.path.exists(gpkg_path), f"GeoPackage not found at {gpkg_path}"

        # Load the polygon GeoPackage layer
        polygon_layer = QgsVectorLayer(f"{gpkg_path}|layername={layer_name}", layer_name, "ogr")
        assert polygon_layer.isValid(), "Failed to load the GeoPackage layer from input_files"

        print("\n[OK] Successfuly loaded the polygon layer from input_files")
        # Path to the configuration file
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "layers_merging_order.csv")
        assert os.path.exists(config_path), f"Configuration file not found: {config_path}"

        wfs_downloader = WFSDownloader(config_path, True, polygon_layer, False)
        layer_list = wfs_downloader.get_ZABAGED_layers_list()

        # Ensure the layer list is not empty
        assert len(layer_list) > 2, f"Expected more than 2 layers, but got {len(layer_list)}"
        print("[OK] Successfuly loaded ZABAGED layers from the configuration file")

        # Load the URL from the ZABAGED.yaml file
        ZABAGED_URL = get_string_from_yaml(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                        "config", "ZABAGED.yaml"), "URL")

        assert ZABAGED_URL, "URL not found in ZABAGED.yaml"
        print("[OK] Successfuly downloaded the ZABAGED layers from WFS")

        # Get extent of the polygon layer
        ymin, xmin, ymax, xmax, extent = wfs_downloader.get_wfs_info(layer_list)
        assert ymin is not None, "failed to get extent from polygon layer"
        print("[OK] Successfuly acquired the extent of the polygon layer")

        ZABAGED_layers = []

        # Download ZABAGED layers from the WFS service
        for layer in layer_list:
            ZABAGED_layers.append(wfs_downloader.process_wfs_layer(layer, ymin, xmin, ymax, xmax, extent, ZABAGED_URL))

        assert len(ZABAGED_layers) > 0, "Failed to download ZABAGED layers"
        print("[OK] Successfuly downloaded ZABAGED layers")

        # Get the LPIS layer from the WFS service
        LPIS_configpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                        "config", "LPIS.yaml")
        LPIS_layername = get_string_from_yaml(LPIS_configpath, "layer_name")
        LPIS_URL = get_string_from_yaml(LPIS_configpath, "URL")

        assert LPIS_layername, "Layer name not found in LPIS.yaml"
        assert LPIS_URL, "URL not found in LPIS.yaml"
        print("[OK] Successfuly loaded the LPIS configuration file")

        response = requests.get(LPIS_URL)
        assert response.status_code == 200, f"Failed to access LPIS URL: {LPIS_URL}"
        print("[OK] Successfully accessed the LPIS URL")
