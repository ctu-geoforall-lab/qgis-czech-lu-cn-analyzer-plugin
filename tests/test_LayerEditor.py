import sys
import os
from qgis.core import QgsApplication, QgsVectorLayer
from utils_for_testing import assert_layers_equal, check_gpkg_layers

# Ensure that qgis packages are imported to your python environment when running locally
# (/usr/lib/python3/dist-packages/qgis)

# Add the parent directory to the PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WFSdownloader import WFSDownloader
from PluginUtils import get_string_from_yaml
from LayerEditor import LayerEditor

# Initialize QGIS application in the main thread
qgs = QgsApplication([], False)
qgs.initQgis()


def check_layer_validity(layer, layer_name, layer_path):
    """Check if a QgsVectorLayer is valid, print errors if necessary."""
    if not layer.isValid():
        print(f"[ERROR] Layer '{layer_name}' is not valid. File: {layer_path}")
        return False

    if layer.crs().isValid():
        print(f"[OK] Layer '{layer_name}' CRS: {layer.crs().authid()}")
    else:
        print(f"[ERROR] Layer '{layer_name}' CRS is not valid!")

    return True


class TestLayerEditor:
    """Test the LayerEditor class"""
    @classmethod
    def teardown_class(cls):
        qgs.exitQgis()

    def test_edit_layers(self):
        """Test the LayerEditor class to edit vector layers"""

        print("\n")
        # Define input file paths
        base_folder = os.path.dirname(__file__)
        input_folder = os.path.join(base_folder, 'input_files', "testing_LayerEditor_data")
        reference_folder = os.path.join(base_folder, 'reference')

        top_layer_path = os.path.join(input_folder, 'top.gpkg')
        mid_layer_path = os.path.join(input_folder, 'mid.gpkg')
        low_layer_path = os.path.join(input_folder, 'low.gpkg')

        # Verify GeoPackage layers exist and contain the expected layers
        check_gpkg_layers(top_layer_path, "top")
        check_gpkg_layers(mid_layer_path, "mid")
        check_gpkg_layers(low_layer_path, "low")

        # Load layers
        TOP_layer = QgsVectorLayer(f"{top_layer_path}|layername=top", "top", "ogr")
        MID_layer = QgsVectorLayer(f"{mid_layer_path}|layername=mid", "mid", "ogr")
        LOW_layer = QgsVectorLayer(f"{low_layer_path}|layername=low", "low", "ogr")

        assert check_layer_validity(TOP_layer, "top", top_layer_path)
        assert check_layer_validity(MID_layer, "mid", mid_layer_path)
        assert check_layer_validity(LOW_layer, "low", low_layer_path)

        # Load reference layers
        top_ref_path = os.path.join(reference_folder, 'top_reference.gpkg')
        mid_ref_path = os.path.join(reference_folder, 'mid_reference.gpkg')
        low_ref_path = os.path.join(reference_folder, 'low_reference.gpkg')

        check_gpkg_layers(top_ref_path, "top_reference")
        check_gpkg_layers(mid_ref_path, "mid_reference")
        check_gpkg_layers(low_ref_path, "low_reference")

        TOP_ref_layer = QgsVectorLayer(f"{top_ref_path}|layername=top_reference", "top_reference", "ogr")
        MID_ref_layer = QgsVectorLayer(f"{mid_ref_path}|layername=mid_reference", "mid_reference", "ogr")
        LOW_ref_layer = QgsVectorLayer(f"{low_ref_path}|layername=low_reference", "low_reference", "ogr")

        assert check_layer_validity(TOP_ref_layer, "top_reference", top_ref_path)
        assert check_layer_validity(MID_ref_layer, "mid_reference", mid_ref_path)
        assert check_layer_validity(LOW_ref_layer, "low_reference", low_ref_path)

        # Load config files
        merging_conf = os.path.join(base_folder, 'input_files', "testing_LayerEditor_conf", 'testing_layers_merging_order.csv')
        test_data_conf = os.path.join(base_folder, 'input_files', "testing_LayerEditor_conf", 'test_data.yaml')
        LU_atr_conf = os.path.join(base_folder, 'input_files', "testing_LayerEditor_conf", 'test_data_to_LandUseCode_table.yaml')

        for conf_path in [merging_conf, test_data_conf, LU_atr_conf]:
            assert os.path.exists(conf_path), f"Config file not found: {conf_path}"
            print(f"[OK] Loaded config file: {conf_path}")

        # Initialize LayerEditor
        wfs_downloader = WFSDownloader(merging_conf, True, LOW_layer, False)
        ymin, xmin, ymax, xmax, ext = wfs_downloader.get_wfs_info(LOW_layer)

        layer_editor = LayerEditor(LU_atr_conf, None, test_data_conf, merging_conf, None, True,
                                   LOW_layer, ymin, xmin, ymax, xmax)

        # Edit the layers
        layer_list = [LOW_layer, MID_layer, TOP_layer]
        layer_list = layer_editor.add_landuse_attribute(layer_list)

        # Validate edited layer against reference layers
        assert_layers_equal(layer_list[0], LOW_ref_layer)
        print("[OK] Base LandUse code mapped.")


        # Update landuse code by attribute
        layer_list = layer_editor.edit_landuse_code(layer_list)
        assert_layers_equal(layer_list[1], MID_ref_layer)
        print("[OK] LandUse code updated successfully.")


        # Buffer layers
        layer_list = layer_editor.buffer_layers(layer_list)
        assert_layers_equal(layer_list[2], TOP_ref_layer)
        print("[OK] Buffering successfully.")






