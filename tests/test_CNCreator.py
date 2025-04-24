import sys
import os
import pytest

from qgis.core import QgsApplication, QgsVectorLayer

# Add the parent directory to the PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from CNCreator import CNCreator
from utils_for_testing import assert_layers_equal, check_gpkg_layers

# Initialize QGIS application in the main thread
qgs = QgsApplication([], False)
qgs.initQgis()


class TestCNCreator:
    """Test the LayerEditor class"""

    @classmethod
    def teardown_class(cls):
        qgs.exitQgis()

    def test_create_cn_layer(self):
        """Test the creation of a CN layer from a given input layer and CN table."""

        base_folder = os.path.dirname(__file__)
        # Path to the input layer
        input_layer_path = os.path.join(base_folder, 'input_files', 'TESTING_ntersected_landuse_and_hsg.gpkg')
        # Path to the CN table
        cn_table_path = os.path.join(base_folder, 'input_files', 'testing_CN_table.csv')

        check_gpkg_layers(input_layer_path, "TESTING_ntersected_landuse_and_hsg")
        print("\n")
        print("[OK] Input layer file exists.")


        InputLayer = QgsVectorLayer(f"{input_layer_path}|layername=TESTING_ntersected_landuse_and_hsg",
                                    "TESTING_ntersected_landuse_and_hsg", "ogr")

        assert InputLayer.isValid(), "Input layer is not valid."
        print("[OK] Input layer is valid.")

        # Create an instance of CNCreator
        cn_creator = CNCreator(InputLayer, cn_table_path)
        # Create the CN layer
        cn_layer = cn_creator.CreateCNLayer()

        # Load the reference layer for comparison
        input_layer_path = os.path.join(base_folder, 'reference', 'TESTING_CNlayer.gpkg')
        check_gpkg_layers(input_layer_path, "cn_layer")
        print("[OK] Reference layer file exists.")

        ReferenceLayer = QgsVectorLayer(f"{input_layer_path}|layername=cn_layer",
                                    "cn_layer", "ogr")
        assert ReferenceLayer.isValid(), "Reference layer is not valid."
        print("[OK] Reference layer is valid.")

        # Check if the CN layer was created successfully
        assert_layers_equal(cn_layer, ReferenceLayer)
        print("[OK] CN layer created successfully and matches the reference layer.")